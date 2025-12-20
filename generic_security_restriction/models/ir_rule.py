# -*- coding: utf-8 -*-
import logging

from odoo import api, models, tools
from odoo.tools import config
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

# Odoo 19+: odoo.fields.Domain (reemplaza odoo.osv.expression.*)
try:
    from odoo.fields import Domain
except Exception:  # pragma: no cover
    Domain = None
    from odoo.osv import expression


def _domain_to_list(d):
    """Return a plain domain list for ORM calls."""
    if Domain and hasattr(d, "to_list"):
        return d.to_list()
    return d


def _domain_and(domains):
    if Domain:
        return Domain.AND(domains)
    return expression.AND(domains)


def _domain_or(domains):
    if Domain:
        return Domain.OR(domains)
    return expression.OR(domains)


def _domain_normalize(dom):
    """
    Normalize a domain coming from safe_eval (string domain).
    In Odoo 19, Domain(dom) normalizes; in older versions use expression.normalize_domain.
    """
    if Domain:
        return Domain(dom)
    return expression.normalize_domain(dom)


class IrRule(models.Model):
    _inherit = "ir.rule"

    def _gsr__model_restriction__domain(self, model_name, mode):
        """
        Build additional restriction domain from generic.security.model.restriction rules.
        - Works in Odoo 19 without relying on res.users.groups_id
        - Avoids res.groups.users / group_ids.user_ids traversals that crash in your build
        """
        if mode == "read":
            mode_domain = [("apply_mode_read", "=", True)]
        elif mode == "write":
            mode_domain = [("apply_mode_write", "=", True)]
        elif mode == "create":
            mode_domain = [("apply_mode_create", "=", True)]
        elif mode == "unlink":
            mode_domain = [("apply_mode_unlink", "=", True)]
        else:
            # Unknown mode, do nothing
            return []

        # 1) Search candidate rules (no user/group filtering here to avoid missing fields)
        restriction_rules_domain = _domain_and([
            mode_domain,
            [("model_name", "=", model_name)],
            [("active", "=", True)],
        ])

        candidates = self.sudo().env["generic.security.model.restriction"].search(
            _domain_to_list(restriction_rules_domain)
        )
        if not candidates:
            return []

        # 2) Filter applicable rules (user_ids OR group_ids)
        uid = self.env.user.id
        applicable = self.env["generic.security.model.restriction"]

        for r in candidates:
            # Assigned directly to user
            if uid in r.user_ids.ids:
                applicable |= r
                continue

            # Assigned by group: use has_group(xmlid) for each group in rule
            ok = False
            for g in r.group_ids:
                xmlid = g.get_external_id().get(g.id)
                if xmlid and self.env.user.has_group(xmlid):
                    ok = True
                    break

            if ok:
                applicable |= r

        if not applicable:
            return []

        # 3) Evaluate restriction domains and AND them together
        eval_context = self._eval_context()
        restriction_domains = []

        for rule in applicable:
            domain_expr = rule._get_restriction_domain()
            dom = safe_eval(domain_expr, eval_context) if domain_expr else []
            dom = _domain_normalize(dom)
            restriction_domains.append(dom)

        combined = _domain_and(restriction_domains)
        return _domain_to_list(combined)

    @api.model
    @tools.conditional(
        "xml" not in config["dev_mode"],
        tools.ormcache(
            "self.env.uid",
            "self.env.su",
            "model_name",
            "mode",
            "tuple(self._compute_domain_context_values())",
        ),
    )
    def _compute_domain(self, model_name, mode="read"):
        domain = super()._compute_domain(model_name, mode=mode)

        # Superuser bypass
        if self.env.su:
            return domain

        model_restriction_domain = self._gsr__model_restriction__domain(
            model_name=model_name, mode=mode
        )
        if not model_restriction_domain:
            return domain

        combined = _domain_and([domain, model_restriction_domain])
        return _domain_to_list(combined)
