const presets = {
  "What is a symptom associated with Type 2 diabetes mellitus?": {
    vector: "A symptom associated with Type 2 diabetes mellitus is frequent urination (polyuria), often accompanied by increased thirst and fatigue.",
    graph: "The knowledge graph links Type 2 diabetes mellitus to the symptom hyperglycemia, with polydipsia and polyuria as connected clinical manifestations.",
    hybrid: "Frequent urination (polyuria) is a symptom of Type 2 diabetes mellitus. It is driven by excess glucose in the blood and commonly appears with increased thirst."
  },
  "What is the relationship between postpartum depression and breastfeeding?": {
    vector: "The retrieved review describes a relationship between postpartum depression and breastfeeding, with depressive symptoms potentially affecting initiation and continuation.",
    graph: "The graph connects postpartum depression with breastfeeding through an associated outcome relationship in the maternal mental health literature.",
    hybrid: "Postpartum depression may make breastfeeding initiation or continuation more difficult, while breastfeeding support is discussed as part of postpartum care.",
    sources: ["“Depressive symptoms can affect breastfeeding initiation and continuation.”", "postpartum depression → ASSOCIATED_WITH → breastfeeding", "Review context and graph relationship agree on a maternal care association."]
  },
  "How does montelukast affect cough variant asthma biomarkers?": {
    vector: "Montelukast improved cough variant asthma symptoms and reduced inflammatory biomarkers including serum IgE and IL-6 in the retrieved study.",
    graph: "The graph connects montelukast sodium to cough variant asthma and to changes in IgE and IL-6, representing the treatment and biomarker paths.",
    hybrid: "Montelukast was associated with improved symptoms and lower IgE and IL-6 compared with the comparison treatment, according to the study context.",
    sources: ["“Montelukast improved clinical symptoms and inflammatory indexes.”", "montelukast → AFFECTS → IgE / IL-6", "Vector biomarker chunk joined with treatment relationship context."]
  }
};

const query = document.querySelector('#query');
const queryLabel = document.querySelector('#query-label');
const run = document.querySelector('#run');
const cards = [...document.querySelectorAll('[data-answer]')];

document.querySelectorAll('.preset').forEach((preset) => {
  preset.addEventListener('click', () => {
    document.querySelectorAll('.preset').forEach((item) => item.classList.remove('active'));
    preset.classList.add('active');
    query.value = preset.textContent.trim();
  });
});

run.addEventListener('click', () => {
  const text = query.value.trim() || 'Enter a question to compare retrieval paths.';
  queryLabel.textContent = text;
  run.disabled = true;
  run.innerHTML = '<span class="play">◌</span> Comparing paths...';
  cards.forEach((card) => { card.style.opacity = '.35'; });
  window.setTimeout(() => {
    const matched = presets[text];
    if (matched) cards.forEach((card) => {
      card.textContent = matched[card.dataset.answer];
      const source = card.closest('.answer-card')?.querySelector('.source');
      if (source && matched.sources) source.textContent = matched.sources[['vector', 'graph', 'hybrid'].indexOf(card.dataset.answer)];
    });
    cards.forEach((card) => { card.style.opacity = '1'; });
    run.disabled = false;
    run.innerHTML = '<span class="play">▶</span> Run comparison';
  }, 650);
});
