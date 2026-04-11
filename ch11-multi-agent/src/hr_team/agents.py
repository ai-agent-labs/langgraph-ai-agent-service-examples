from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from hr_team.config import get_settings
from hr_team.tools import BENEFIT_TOOLS, LEAVE_TOOLS


def create_leave_agent():
    """휴가/연차 전문 에이전트 생성."""
    settings = get_settings()
    model = init_chat_model(
        model_provider="openai",
        model=settings.default_model,
        temperature=settings.temperature,
    )

    return create_agent(
        model=model,
        tools=LEAVE_TOOLS,
        name="leave_agent",
        system_prompt="당신은 휴가/연차 전문 상담사입니다. 잔여 연차 조회와 휴가 신청을 담당합니다.",
    )


def create_benefit_agent():
    """복리후생 전문 에이전트 생성."""
    settings = get_settings()
    model = init_chat_model(
        model_provider="openai",
        model=settings.default_model,
        temperature=settings.temperature,
    )

    return create_agent(
        model=model,
        tools=BENEFIT_TOOLS,
        name="benefit_agent",
        system_prompt="당신은 복리후생 전문 상담사입니다. 건강검진, 교육비 등 복지 프로그램을 안내합니다.",
    )
