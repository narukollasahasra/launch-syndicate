import streamlit as st
import os
import time
import json
from groq import Groq


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Idiofy Launch Syndicate",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Idiofy Launch Syndicate")

st.write(
    "Multi-Agent Orchestration: Scoping a 4-week V1 launch "
    "by balancing Product Management and Brand Strategy."
)


# ============================================================
# GROQ API CONFIGURATION
# ============================================================

api_key = os.environ.get("GROQ_API_KEY")

if not api_key and "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]

if not api_key:
    st.error(
        "⚠️ Groq API Key missing! Please configure "
        "GROQ_API_KEY in Streamlit Secrets."
    )
    st.stop()

client = Groq(api_key=api_key)


# ============================================================
# AGENT RUNNER
# ============================================================

def run_agent(persona, prompt_input, json_mode=False):
    start_time = time.time()

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": persona
            },
            {
                "role": "user",
                "content": prompt_input
            }
        ],
        temperature=0.2,
        response_format=(
            {"type": "json_object"}
            if json_mode
            else {"type": "text"}
        )
    )

    latency = round(time.time() - start_time, 2)

    return response.choices[0].message.content, latency


# ============================================================
# USER INPUT
# ============================================================

raw_idea = st.text_input(
    "Enter your raw product or startup idea:",
    value=(
        "A mobile app connecting local bakers with people "
        "who want custom birthday cakes."
    )
)


# ============================================================
# START MULTI-AGENT WORKFLOW
# ============================================================

if st.button(
    "Initiate Multi-Agent Launch Sprint",
    type="primary"
):

    if not raw_idea:
        st.warning("Please provide an idea.")

    else:

        total_latency = 0

        # ----------------------------------------------------
        # STATUS CONTAINER
        # ----------------------------------------------------

        with st.status(
            "Orchestrating Agency Team...",
            expanded=True
        ) as status:

            # =================================================
            # AGENT 1 — MARKET RESEARCHER
            # =================================================

            st.write(
                "🔍 **Agent 1 (Market Researcher):** "
                "Analyzing target audience..."
            )

            researcher_prompt = """
You are a Market Researcher.

INPUT: A raw product idea.

OUTPUT FORMAT: Return exactly 3 bullet points:
- Target Audience: [who it is for]
- Market Gap: [what is missing currently]
- Core Problem: [the primary pain point]

Do not add any conversational text.
"""

            research, lat1 = run_agent(
                researcher_prompt,
                f"RAW IDEA:\n{raw_idea}"
            )

            total_latency += lat1

            # =================================================
            # AGENT 2 — TECHNICAL PRODUCT MANAGER
            # =================================================

            st.write(
                "⚙️ **Agent 2 (Tech PM):** "
                "Scoping the 4-week functional V1..."
            )

            tech_pm_prompt = """
You are a Technical Product Manager.

INPUT: Market Research data.

OUTPUT FORMAT: Return exactly 3 core MVP features
that can be built in 4 weeks.

Format as:
1. [Feature Name]: [Brief description]
2. [Feature Name]: [Brief description]
3. [Feature Name]: [Brief description]

Ruthlessly cut feature bloat.
"""

            tech_scope, lat2 = run_agent(
                tech_pm_prompt,
                f"RESEARCH:\n{research}"
            )

            total_latency += lat2

            # =================================================
            # AGENT 3 — BRAND STRATEGIST
            # =================================================

            st.write(
                "✨ **Agent 3 (Brand Strategist):** "
                "Developing core messaging..."
            )

            brand_prompt = """
You are a Brand Strategist.

INPUT: Market Research data.

OUTPUT FORMAT: Return exactly two lines:

Brand Positioning: [2 sentence value proposition]
Brand Tone: [3 keywords, e.g., Playful, Trustworthy, Bold]
"""

            brand_strategy, lat3 = run_agent(
                brand_prompt,
                f"RESEARCH:\n{research}"
            )

            total_latency += lat3

            # =================================================
            # AGENT 4 — QUALITY GATE CRITIC
            # =================================================

            st.write(
                "⚖️ **Agent 4 (Quality Gate Critic):** "
                "Identifying conflicts..."
            )

            critic_prompt = """
You are a Quality Gate Critic.

INPUT: Tech PM scope and Brand Strategy.

OUTPUT FORMAT: Return a short paragraph identifying
any conflicts between the technical scope and brand promises.

If none, state:
'No conflicts identified'
"""

            critique, lat4 = run_agent(
                critic_prompt,
                f"""
TECH SCOPE:
{tech_scope}

BRAND STRATEGY:
{brand_strategy}
"""
            )

            total_latency += lat4

            # =================================================
            # AGENT 5 — LEAD SYNTHESIZER
            # =================================================

            st.write(
                "🚀 **Agent 5 (Lead Synthesizer):** "
                "Finalizing Go-To-Market Brief..."
            )

            reviser_prompt = """
You are the Lead Synthesizer for the Idiofy product agency.

Take the critique, resolve the conflicts, and output
a structured JSON Go-To-Market Launch Brief.

Schema:

{
    "product_name": "string",
    "target_audience": "string",
    "four_week_v1_features": ["list of strict MVP features"],
    "brand_positioning": "string",
    "resolved_tradeoffs": "string explaining how the critic's concerns were solved"
}
"""

            final_brief, lat5 = run_agent(
                reviser_prompt,
                f"""
TECH:
{tech_scope}

BRAND:
{brand_strategy}

CRITIQUE:
{critique}
""",
                json_mode=True
            )

            total_latency += lat5

            # ------------------------------------------------
            # FINISH STATUS
            # ------------------------------------------------

            status.update(
                label=(
                    f"🚀 Launch Sprint Complete! "
                    f"Total Latency: {round(total_latency, 2)}s"
                ),
                state="complete",
                expanded=False
            )


        # ====================================================
        # AGENT OUTPUTS
        # ====================================================

        st.subheader("📊 Agent Outputs")

        # IMPORTANT:
        # These expanders are OUTSIDE st.status()
        # to avoid Streamlit nested element errors.

        with st.expander(
            f"🔍 Research Data ({lat1}s)"
        ):
            st.write(research)

        with st.expander(
            f"⚙️ Tech Scope ({lat2}s)"
        ):
            st.write(tech_scope)

        with st.expander(
            f"✨ Brand Strategy ({lat3}s)"
        ):
            st.write(brand_strategy)

        with st.expander(
            f"⚖️ Critique ({lat4}s)"
        ):
            st.write(critique)


        # ====================================================
        # FINAL GO-TO-MARKET BRIEF
        # ====================================================

        st.divider()

        try:

            json_data = json.loads(final_brief)

            product_name = json_data.get(
                "product_name",
                "Unnamed Product"
            )

            target_audience = json_data.get(
                "target_audience",
                ""
            )

            features = json_data.get(
                "four_week_v1_features",
                []
            )

            brand_positioning = json_data.get(
                "brand_positioning",
                ""
            )

            resolved_tradeoffs = json_data.get(
                "resolved_tradeoffs",
                ""
            )


            st.subheader(
                f"🚀 {product_name} - Go-To-Market Brief"
            )


            st.write(
                f"**Target Audience:** {target_audience}"
            )


            st.markdown(
                "**4-Week Functional V1 Features:**"
            )

            for feature in features:
                st.markdown(
                    f"- {feature}"
                )


            st.info(
                f"**Brand Positioning:** "
                f"{brand_positioning}"
            )


            st.warning(
                f"**Resolved Tradeoffs:** "
                f"{resolved_tradeoffs}"
            )


        except Exception:

            st.subheader(
                "🚀 Go-To-Market Brief"
            )

            st.markdown(final_brief)
