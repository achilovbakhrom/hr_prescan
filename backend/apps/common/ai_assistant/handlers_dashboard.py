"""Handlers for dashboard and subscription AI assistant operations."""

from apps.common.ai_assistant.resolvers import resolve_vacancy


def handle_get_dashboard(*, user, params):
    from apps.common.selectors import get_dashboard_stats

    stats = get_dashboard_stats(company=user.company)
    return {
        "success": True,
        "message": "Here are your dashboard stats.",
        "data": stats,
        "action": "get_dashboard",
    }


def handle_get_vacancy_summary(*, user, params):
    from apps.applications.models import Application
    from apps.interviews.models import Interview

    vacancy = resolve_vacancy(user=user, title=params.get("vacancy_title", ""))

    total_candidates = Application.objects.filter(
        vacancy=vacancy,
        is_deleted=False,
    ).count()
    by_status = {}
    for s in Application.Status:
        count = Application.objects.filter(
            vacancy=vacancy,
            is_deleted=False,
            status=s.value,
        ).count()
        if count > 0:
            by_status[s.value] = count

    pending_interviews = Interview.objects.filter(
        application__vacancy=vacancy,
        status=Interview.Status.PENDING,
    ).count()
    completed_interviews = Interview.objects.filter(
        application__vacancy=vacancy,
        status=Interview.Status.COMPLETED,
    ).count()

    data = {
        "id": str(vacancy.id),
        "title": vacancy.title,
        "status": vacancy.status,
        "total_candidates": total_candidates,
        "candidates_by_status": by_status,
        "pending_interviews": pending_interviews,
        "completed_interviews": completed_interviews,
    }
    return {
        "success": True,
        "message": f"Summary for '{vacancy.title}'.",
        "data": data,
        "action": "get_vacancy_summary",
    }


def handle_get_subscription_info(*, user, params):
    from apps.subscriptions.selectors import get_user_subscription

    subscription = get_user_subscription(user=user)
    if subscription is None:
        return {
            "success": True,
            "message": "No active subscription found.",
            "data": {"has_subscription": False},
            "action": "get_subscription_info",
        }
    data = {
        "has_subscription": True,
        "plan": subscription.plan.name,
        "tier": subscription.plan.tier,
        "billing_period": subscription.billing_period,
        "is_active": subscription.is_active,
        "current_period_end": subscription.current_period_end.isoformat(),
    }
    return {
        "success": True,
        "message": f"You are on the {subscription.plan.name} plan.",
        "data": data,
        "action": "get_subscription_info",
    }


def handle_get_usage(*, user, params):
    from apps.subscriptions.services import get_subscription_usage

    usage = get_subscription_usage(user=user)
    return {
        "success": True,
        "message": "Here is your current usage.",
        "data": usage,
        "action": "get_usage",
    }
