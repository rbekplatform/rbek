from __future__ import annotations

from crewai import Agent, Crew, Process, Task

from governed_tool import RBEKGovernedWeatherTool


def build_crewai_reference(
    tool: RBEKGovernedWeatherTool,
) -> tuple[Agent, Task, Crew]:
    agent = Agent(
        role="Weather operations agent",
        goal=(
            "Use the governed weather tool when "
            "weather execution is required."
        ),
        backstory=(
            "A deterministic CrewAI reference agent "
            "whose external action is governed by RBEK."
        ),
        tools=[tool],
        verbose=False,
        allow_delegation=False,
    )

    task = Task(
        description=(
            "Use the governed weather tool for the "
            "provided latitude and longitude."
        ),
        expected_output=(
            "A governed RBEK execution result."
        ),
        agent=agent,
        tools=[tool],
    )

    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=False,
    )

    return agent, task, crew
