import streamlit as st
from vector.run_vector import run_vector_query
from graph.run_graph import run_graph_query
from hybrid.run_hybrid import run_hybrid_query

st.set_page_config(page_title="HealthRAG", layout="wide")
st.title("HealthRAG Evaluation")

# ---- Inputs ----
questions = [
"According to the provided contexts, what are the general and specific factors associated with depressive disorders in people living with HIV, considering both the broader impacts on their lives and the specific demographic and clinical characteristics linked to the condition?",
"According to the review, what is a proposed mechanism by which fructose exposure might contribute to pediatric atopic disease, and how do epidemiologic findings on this link vary?",
"According to the provided contexts, what is the effect of antenatal psychological interventions on postpartum depression outcomes and incidence rates in pregnant women?",
"What is the primary therapeutic goal of the randomized controlled trial investigating Huangqi Guizhi Wuwu Decoction in non-small cell lung cancer patients with leptomeningeal metastases undergoing intrathecal Pemetrexed chemotherapy, given the limitations of this treatment?",
"Considering the efficacy and safety of novel antidiabetic drugs for type 2 diabetes and chronic kidney disease as detailed in the network meta-analysis, how do glucagon-like peptide-1 receptor agonists contribute to the management of diabetic kidney disease, and what does emerging evidence suggest about their combination therapy?",
##"In adult patients with Type 2 Diabetes Mellitus inadequately controlled on metformin monotherapy, what was the observed superiority of the fixed-dose combination of glimepiride, voglibose, and extended-release metformin compared to other combinations in reducing hyperglycemia?",
"Considering the potential for amplified immune-related adverse events when immune checkpoint inhibitors are used concurrently with other medications, as highlighted in the case report and literature review, what specific drug-induced adverse events are suggested to be exacerbated by this combination?",
"In the randomized controlled trial exploring the effectiveness of functional near-infrared spectroscopy-guided neurofeedback combined with art therapy and cognitive behavioral therapy for post-stroke depression, what were the secondary outcome measures related to inflammatory markers, specifically concerning TNF-alpha levels?",
"In the context of Type 2 diabetes mellitus and its management, how does the study investigating Glimepiride, Voglibose, and Metformin ER relate to changes in HbA1c levels, considering the prevalence of T2DM in India and the general characteristics of the disease?",
"Given that unhealthy lifestyles contribute to Type 2 diabetes mellitus, what specific glycemic marker, besides fasting blood glucose and HOMA-IR, is being evaluated as a potential outcome in patients with T2DM receiving mangosteen peel extract supplementation?",
"What are the benefits of psychosocial interventions that treat borderline personality disorder, psychosis, and mental illness, and how are they associated with patient engagement?",
"What conditions do glucagon-like peptide-1 receptor agonists treat, and what risk factor are they associated with, according to the provided text?",
"What are the key terms mentioned in relation to cognitive impairment in type 2 diabetes, including other specific neurological conditions and the general phenomenon of cognitive dysfunction?",
"What are the potential adverse events associated with immune checkpoint inhibitors, and what serious conditions do they treat?",
"What is the association between magnesium levels and diabetic retinopathy in type 2 diabetes, and what is the certainty of this evidence?",
"What are the cognitive implications associated with inflammatory markers, considering both their potential role as a risk factor for adverse effects and their association with specific types of cognitive changes?",
"What were the overall effects of probiotics on patients with substance-induced depressive disorder, considering their impact on depressive symptoms, anxiety, and inflammatory markers?",
"Based on the systematic review and meta-analysis, what are the primary outcomes measured, and which psychological symptoms or conditions are reported to be ameliorated by antenatal psychological interventions during pregnancy?",
"What factors were associated with low-dose CT uptake for lung cancer screening among high-risk populations, according to this systematic review and meta-analysis, and how did these factors influence the outcomes?",
"What are the comparative efficacy and cognitive safety profiles of Magnetic Seizure Therapy (MST) versus right unilateral ultra-brief electroconvulsive therapy (RUL-UB ECT) for patients with depression and major depressive disorder, as indicated by their respective primary outcomes?",
##"What is the breakdown of algorithms identified in the systematic review for identifying asthma patients, specifically in terms of those identifying general asthma, asthma exacerbations, and those characterizing asthma severity or control?",
##"What are the primary risks and complications associated with the use of cerebral embolic protection devices, beyond the initial concern of embolic debris?",
"Comparing the prevalence of different respiratory viruses in acute asthma across age groups, which viruses were more common in children compared to adults, and vice versa?",
"How does montelukast sodium affect symptoms and biomarkers in patients with cough variant asthma due to wind cold attacking the lung, and what is its comparative effect on serum levels of IgE and IL-6 compared to wheat-grain blistering moxibustion?",
"What are the combined therapeutic benefits of sodium-glucose cotransporter-2 inhibitors, specifically in relation to treating chronic conditions and mortality?",
"What are the cognitive conditions and biomarkers that dulaglutide is associated with, and does it show a treatment effect for any of them?",
"What are the key psychological outcomes and sleep-related measures that are mediated by the Transdiagnostic Intervention for Sleep and Circadian Dysfunction (TSC), and how do insomnia symptom severity and sleep parameters individually and jointly contribute to these mediations in the context of major depressive disorder?",
"What is the therapeutic relationship between Benzodiazepines (BZDs) and Cognitive Behavioral Therapy (CBT) in the treatment of depression, and how does this compare to monotherapy approaches?",
"What are the relationships between Pemetrexed, non-small cell lung cancer, and neurotoxicity, considering its therapeutic use and potential adverse effects?"

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