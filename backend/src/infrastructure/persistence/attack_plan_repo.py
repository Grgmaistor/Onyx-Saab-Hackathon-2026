from __future__ import annotations

import json
from src.domain.entities.attack_plan import AttackPlan
from .database import get_session
from .models import AttackPlanModel


class AttackPlanRepo:

    def save(self, plan: AttackPlan) -> str:
        session = get_session()
        try:
            existing = session.query(AttackPlanModel).get(plan.id)
            if existing:
                existing.name = plan.name
                existing.source = plan.source.value
                existing.description = plan.description
                existing.created_at = plan.created_at
                existing.tags_json = json.dumps(plan.tags)
                existing.plan_json = json.dumps(plan.to_dict())
            else:
                session.add(AttackPlanModel(
                    plan_id=plan.id,
                    name=plan.name,
                    source=plan.source.value,
                    description=plan.description,
                    created_at=plan.created_at,
                    tags_json=json.dumps(plan.tags),
                    plan_json=json.dumps(plan.to_dict()),
                ))
            session.commit()
            return plan.id
        finally:
            session.close()

    def get(self, plan_id: str) -> AttackPlan | None:
        session = get_session()
        try:
            m = session.query(AttackPlanModel).get(plan_id)
            if not m:
                return None
            return AttackPlan.from_dict(json.loads(m.plan_json))
        finally:
            session.close()

    def list_all(self, source: str | None = None) -> list[AttackPlan]:
        session = get_session()
        try:
            q = session.query(AttackPlanModel)
            if source:
                q = q.filter_by(source=source)
            return [AttackPlan.from_dict(json.loads(m.plan_json))
                    for m in q.order_by(AttackPlanModel.created_at.desc()).all()]
        finally:
            session.close()

    def delete(self, plan_id: str) -> bool:
        session = get_session()
        try:
            m = session.query(AttackPlanModel).get(plan_id)
            if not m:
                return False
            session.delete(m)
            session.commit()
            return True
        finally:
            session.close()

    def count_by_source(self) -> dict[str, int]:
        session = get_session()
        try:
            from sqlalchemy import func
            rows = session.query(
                AttackPlanModel.source, func.count(AttackPlanModel.plan_id)
            ).group_by(AttackPlanModel.source).all()
            return {row[0]: row[1] for row in rows}
        finally:
            session.close()
