import streamlit as st
from vector.run_vector import run_vector_query
from graph.run_graph import run_graph_query
from hybrid.run_hybrid import run_hybrid_query

st.set_page_config(page_title="HealthRAG", layout="wide")
st.title("HealthRAG Evaluation")

# ---- Inputs ----
questions = [
"What is the study about regarding Huangqi Guizhi Wuwu decoction and intrathecal Pemetrexed chemotherapy?",
"What is the efficacy and safety of direct oral anticoagulants compared to heparin in pediatric patients, according to the systematic review and meta-analysis?",
"Does the systematic review and meta-analysis titled 'Antenatal psychological interventions may ameliorate postpartum depression' mention mindfulness as a type of prenatal psychological intervention?",
"What is the relationship between postpartum depression and breastfeeding?",
"What medical databases were searched in the systematic review and meta-analysis titled 'Effects of Transcranial Magnetic Stimulation on Patients with Major Depressive Disorder'?",
#"What is the title of the paper that assessed the safety and tolerability of beclometasone dipropionate/formoterol fumarate/glycopyrronium with the HFA-152a propellant?",
"What medical concepts were searched for in the meta-analysis study on the effect of education on deep vein thrombosis in orthopedic surgery patients?",
"What are the primary outcomes measured in the systematic review titled 'Optimal Strategy of Resistance Training Combined With Other Rehabilitation Interventions for Lower-Limb Dysfunction in Stroke Patients'?",
"What are the observed benefits of combining pharmacotherapy with family-focused therapy or structured psychoeducation for early BD, specifically concerning treatment discontinuation?",
###"What compounds were identified as high-abundance peaks in the Huiyang Shengji unguent according to UPLC-MS/MS analysis?",
"What are the observed changes in pulmonary function indexes, such as FEV1 and PEF, in patients with cough variant asthma of wind cold attacking the lung treated with modified painless wheat-grain blistering moxibustion?",
"According to the systematic review on heart failure therapies in Brazil, what is the incremental cost-effectiveness ratio (ICER) of spironolactone for patients with reduced ejection fraction from the SUS perspective?",
"What impact did the synbiotic Bactecal® have on patients with uncontrolled asthma?",
"What is a symptom associated with Type 2 diabetes mellitus?",
"What is the risk ratio for major bleeding events in pediatric patients treated with DOACs compared to standard of care, according to the systematic review and meta-analysis?",
##"What is the association between parental involvement and depressive symptoms?",
"What is canagliflozin associated with reducing, according to the provided context?",
"What is the relationship between ferroptosis and POU2F3 in the context of small cell lung cancer?",
##"In a double-blind randomized controlled trial of subcutaneous immunotherapy with house dust mite extract in Indonesian children with allergic rhinitis and asthma, what was the observed trend of specific IgE levels?",
"What percentage of pregnant women experience dyspnea during pregnancy, according to the introduction of the paper on spirometry safety?",
"What medical condition is mentioned as requiring new therapies and potentially benefiting from probiotics as an adjunctive strategy?",
"What is the name of the randomized controlled trial that investigated functional near-infrared spectroscopy-guided neurofeedback combined with art therapy and cognitive behavioral therapy for post-stroke depression?",
"What is the efficacy of gefitinib in treating CNS metastases in patients with advanced EGFR-mutated non-small cell lung cancer?",
"What is the effect of patient education on the development of deep vein thrombosis in patients undergoing orthopedic surgery?",
"What is the role of glimepiride in managing Type 2 diabetes mellitus based on the provided context?",
"What psychiatric treatment augmentation was more effective for patients with increased appetite in Level 2 of STAR*D, according to the paper 'Learning Outcomes That Maximally Differentiate Psychiatric Treatments.'?",
"What therapeutic benefit do SGLT2is and GLP-1RA combination therapies offer in patients with type 2 diabetes and albuminuria?",
"What is the effect of mangosteen peel extract on insulin sensitivity in individuals with Type 2 Diabetes Mellitus, according to a systematic review of human studies?",
"What is the known association between transcatheter aortic valve implantation and stroke?",
"What potential mechanisms are suggested for Hui Yang Shengji unguent in promoting wound healing in patients with Yin syndrome and diabetic foot?",
"Considering that maternal autoimmune diseases are linked to an increased risk of asthma in offspring, what is the potential relevance of asthma exacerbations during pregnancy to the common symptom of dyspnea in pregnant women?",
####"According to the systematic review on endodontic treatment of teeth with apical periodontitis and cardiovascular risk, what are the confounding factors mentioned that are linked to increased systemic inflammatory burden in the context of apical periodontitis?",
##"What does the analysis of scientific production on asthma-COPD overlap syndrome reveal about the current research landscape for this condition compared to separate research on asthma and COPD?",
"Based on the provided contexts discussing a systematic review and meta-analysis on direct oral anticoagulants, what was the observed difference in bleeding events between continuous and interrupted DOAC use for minimal bleeding-risk surgical procedures, considering potential selection bias in the findings?",
"Does peppermint oil have any relevance in managing hypertension, which in turn could potentially impact the risk of atherosclerotic cardiovascular disease?",
"In the context of Type 2 diabetes mellitus, how does the efficacy of a fixed-dose combination including glimepiride, voglibose, and extended-release metformin compare to other metformin combinations, given that hyperglycemia is a characteristic symptom?",
#"Considering that MASH is a progressive form of MASLD linked to type 2 diabetes mellitus, what therapeutic option has shown promise due to its metabolic effects and potential hepatic benefits, and how was the evidence for this reviewed?",
"What was the reported difference in systolic blood pressure at 20 days between the trial arm and placebo, given that the trial enrolled patients with systolic blood pressure between 130 and 160 mm Hg?",
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
"What are the relationships between Pemetrexed, non-small cell lung cancer, and neurotoxicity, considering its therapeutic use and potential adverse effects?",
"According to the systematic review on direct oral anticoagulants in pediatric patients, which outcomes showed no statistically significant difference between DOACs and standard of care?",
"In the trial investigating peppermint oil for hypertension, what cardiovascular outcome was explicitly NOT assessed as a primary endpoint?",
"In the network meta-analysis on novel antidiabetic drugs for type 2 diabetes and chronic kidney disease, which drug class was NOT ranked first for reducing hypoglycemic events?",
"In the RCT comparing MST with RUL-UB ECT, what cognitive outcome did MST fail to demonstrate a statistically significant improvement on compared to ECT?",
"Considering that immune checkpoint inhibitors amplify T-cell-mediated drug responses, what concurrent medication use is implicitly contraindicated based on the case report involving moxifloxacin?",
"Given that intrathecal Pemetrexed chemotherapy causes neurotoxicity as a dose-limiting adverse effect, for what patient profile would escalating Pemetrexed dosing be most problematic?",
"According to the systematic review on asthma management during pregnancy, what is the inconsistency in findings regarding whether asthma exacerbations are associated with pre-eclampsia and low birth weight?",
"In the meta-analysis on continuous versus interrupted DOAC use, why did the apparent benefit of continuous use in observational data disappear in high-quality randomised trials?",
"What is the full chemical name of the triple combination inhaler being evaluated as an alternative to HFA-134a propellant in the beclometasone dipropionate study?",
"What are the three specific plasma biomarkers — including their abbreviated forms — measured to assess Alzheimer's disease and related dementia risk in the dulaglutide REWIND trial analysis?",
"What was the exact SUCRA score for dapagliflozin plus exenatide in reducing hypoglycemic events, according to the network meta-analysis on novel antidiabetic drugs?",
"In the systematic review on respiratory viruses in acute asthma, what was the exact percentage prevalence of rhinovirus in adults compared to children, and what was the absolute difference between these two figures?"
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