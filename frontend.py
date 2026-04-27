import streamlit as st
from vector.run_vector import run_vector_query
from graph.run_graph import run_graph_query
from hybrid.run_hybrid import run_hybrid_query

st.set_page_config(page_title="HealthRAG", layout="wide")
st.title("HealthRAG Evaluation")

# ---- Inputs ----
questions = [
    # Single-hop
    "What glucose-related property do SGLT2 inhibitors offer?",
    "Which two aspects related to inhaler prescribing and use are associated with preventable asthma deaths?",
    "What pharmacological class does tirzepatide belong to?",
    "What outcome improvements were observed with nurse-led rehabilitation in asthma patients?",
    "What type of training remains fundamental in stroke rehabilitation?",
    "What disease were cognitive-behavioral therapy and psychodynamic therapy compared for?",
    "What role does vitamin D deficiency play in diabetic peripheral neuropathy?",

    # Multi-hop (valid)
    "How does vitamin D deficiency influence both the presence and severity of diabetic peripheral neuropathy?",
    "How does nurse-led rehabilitation improve both asthma control and quality of life?",
    "What mechanisms are suggested to explain the benefits of SGLT2 inhibitors beyond glucose control?",
    "How does asthma control during pregnancy relate to pregnancy complications such as pre-eclampsia?",

    # Comparative
    "How does combination therapy (psychotherapy + pharmacotherapy) compare to monotherapy in treating depression?",
    "How do nurse-led rehabilitation interventions compare to usual care in asthma management?",
    "How do SGLT2 inhibitors compare with traditional glucose-lowering therapies in terms of additional benefits?",

    # Limitations / gaps
    "What specific long-term effects of tirzepatide in type 1 diabetes are not clearly established?",
    "What aspects of stroke rehabilitation outcomes remain uncertain based on current evidence?",
    "What evidence is lacking regarding the long-term effectiveness of nurse-led asthma rehabilitation?",
    "What limitations exist in current studies linking vitamin D supplementation to neuropathy improvement?",

    "How does type 2 diabetes contribute to diaphragmatic dysfunction, and how does the choice of ventilation mode (PCV-VG vs VCV) influence postoperative respiratory outcomes?",
    "How does the combination therapy of glimepiride, voglibose, and metformin compare to dual therapies in improving glycemic control, and what safety outcomes are associated with these treatments?",
    "How does type 2 diabetes lead to complications such as diabetic foot ulcers, and how do emerging therapies like autologous cell treatment improve healing outcomes?",
    "How do heparin and direct oral anticoagulants differ in their effects on thromboembolic events, and what differences are seen in major and minor bleeding outcomes?",
    "Which neurodegeneration biomarker showed a significant reduction after dulaglutide treatment in participants with elevated baseline levels?",
    
    "What effect did the synbiotic Bactecal® have on FEV1/FVC in patients with asthma?"
]

selected_question = st.selectbox("Select Evaluation Question", questions)
custom_query = st.text_input("Or enter your own question:")

query = custom_query.strip() if custom_query.strip() else selected_question


# ---- RAG wrappers ----
def run_vector_rag(query):
    vector_ans = run_vector_query(query)
    return {
        "answer": vector_ans["answer"]
    }

def run_graph_rag(query):
    graph_ans = run_graph_query(query)
    return {
        "answer": graph_ans["answer"]
    }

def run_hybrid_rag(query):
    hybrid_ans = run_hybrid_query(query)
    return {
        "answer": hybrid_ans["answer"]
    }


# ---- Run ----
if st.button("Run Evaluation"):

    st.write(f"**Query Used:** {query}")

    # ---- Create 3 columns ----
    col1, col2, col3 = st.columns(3)

    # ---- Placeholders ----
    with col1:
        st.subheader("🔍 Vector RAG")
        vec_placeholder = st.empty()
        vec_placeholder.info("Running...")

    with col2:
        st.subheader("🧬 Graph RAG")
        graph_placeholder = st.empty()
        graph_placeholder.info("Waiting...")

    with col3:
        st.subheader("⚡ Hybrid RAG")
        hybrid_placeholder = st.empty()
        hybrid_placeholder.info("Waiting...")


    # =========================
    # STEP 1: VECTOR
    # =========================
    vector_output = run_vector_rag(query)
    vec_placeholder.subheader("🔍 Vector RAG")
    vec_placeholder.write(vector_output["answer"])


    # =========================
    # STEP 2: GRAPH
    # =========================
    graph_output = run_graph_rag(query)
    graph_placeholder.subheader("🧬 Graph RAG")
    graph_placeholder.write(graph_output["answer"])


    # =========================
    # STEP 3: HYBRID
    # =========================
    hybrid_output = run_hybrid_rag(query)
    hybrid_placeholder.subheader("⚡ Hybrid RAG")
    hybrid_placeholder.write(hybrid_output["answer"])