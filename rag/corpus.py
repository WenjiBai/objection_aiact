"""Seed EU AI Act corpus — hand-curated chunks indexed by the RAG layer.

Each chunk corresponds to one `Reference`. Articles + recitals + Annex III
entries that the two demo cases (and the 13 symbolic rules) will retrieve.
Person B can expand this once the full Regulation 2024/1689 text is chunked.
"""

from __future__ import annotations

from shared.schema import Reference, SourceType


# Each entry is what `retrieve()` returns. The `code` is the global handle the
# rest of the system uses (allegations, rule_firings, missing_evidence …).
SEED_CHUNKS: list[Reference] = [
    # -------------------------------------------------- Article 5 (prohibited)
    Reference(
        code="R-Art-5", article_no="5",
        title="Prohibited AI practices",
        snippet=("AI practices including subliminal manipulation, exploiting "
                 "vulnerabilities, social scoring leading to detrimental treatment, "
                 "and emotion recognition in the workplace or education are prohibited."),
        full_text=(
            "Article 5 — Prohibited AI practices. The placing on the market, the "
            "putting into service or the use of AI systems that deploy subliminal "
            "techniques beyond a person's consciousness, exploit any vulnerabilities "
            "of a specific group, evaluate or classify natural persons or groups "
            "based on social behaviour (social scoring) leading to detrimental or "
            "unfavourable treatment, or infer emotions of a natural person in the "
            "areas of workplace and education institutions, are prohibited."
        ),
        source_type=SourceType.LEGISLATION,
        source_label="EU AI Act 2024/1689",
        url="https://eur-lex.europa.eu/eli/reg/2024/1689/oj",
    ),

    # ------------------------------------------------ Article 6 (high-risk class)
    Reference(
        code="R-Art-6", article_no="6",
        title="Classification rules for high-risk AI systems",
        snippet=("An AI system shall be considered high-risk where it is listed in "
                 "Annex III or used as a safety component of a product covered by Annex I."),
        full_text=(
            "Article 6 — Classification rules for high-risk AI systems. An AI system "
            "shall be considered to be high-risk where (a) it is intended to be used "
            "as a safety component of a product, or it is itself a product, covered "
            "by Union harmonisation legislation listed in Annex I, and (b) it is "
            "required to undergo a third-party conformity assessment. AI systems "
            "referred to in Annex III shall also be considered high-risk. Article "
            "6(3) lists narrow exemptions where a high-risk-listed system is not "
            "considered high-risk in practice."
        ),
        source_type=SourceType.LEGISLATION, source_label="EU AI Act 2024/1689",
    ),

    # ------------------------------------------- Article 9 (risk management)
    Reference(
        code="R-Art-9", article_no="9",
        title="Risk management system",
        snippet=("Providers of high-risk AI systems shall establish, implement, "
                 "document and maintain a risk management system across the AI "
                 "lifecycle."),
        full_text=(
            "Article 9 — Risk management system. A risk management system shall be "
            "established, implemented, documented and maintained in relation to "
            "high-risk AI systems. It shall consist of a continuous iterative "
            "process planned and run throughout the entire lifecycle of the AI "
            "system, requiring regular systematic review and updating, including "
            "identification and analysis of foreseeable risks and adoption of "
            "appropriate risk-management measures."
        ),
        source_type=SourceType.LEGISLATION, source_label="EU AI Act 2024/1689",
    ),

    # ------------------------------------------- Article 12 (record-keeping)
    Reference(
        code="R-Art-12", article_no="12",
        title="Record-keeping (lifecycle logging)",
        snippet=("High-risk AI systems shall technically allow for the automatic "
                 "recording of events (logs) over the duration of the system's lifetime."),
        full_text=(
            "Article 12 — Record-keeping. High-risk AI systems shall be designed and "
            "developed with capabilities enabling the automatic recording of events "
            "(logs) over their lifetime. Logging capabilities shall enable the "
            "identification of risks, the monitoring of operation, and post-market "
            "monitoring. Logs shall be retained for at least six months by deployers."
        ),
        source_type=SourceType.LEGISLATION, source_label="EU AI Act 2024/1689",
    ),

    # ----------------------------------- Article 13 (transparency to deployers)
    Reference(
        code="R-Art-13", article_no="13",
        title="Transparency and provision of information to deployers",
        snippet=("High-risk AI systems shall be designed so deployers can interpret "
                 "the system's output and use it appropriately, including via "
                 "comprehensible instructions for use."),
        full_text=(
            "Article 13 — Transparency and provision of information to deployers. "
            "High-risk AI systems shall be designed and developed in such a way that "
            "their operation is sufficiently transparent to enable deployers to "
            "interpret the system's output and use it appropriately. They shall be "
            "accompanied by instructions for use providing information that is "
            "concise, complete, correct and clear."
        ),
        source_type=SourceType.LEGISLATION, source_label="EU AI Act 2024/1689",
    ),

    # ------------------------------------------- Article 14 (human oversight)
    Reference(
        code="R-Art-14", article_no="14",
        title="Human oversight",
        snippet=("High-risk AI systems shall be designed and developed so they can "
                 "be effectively overseen by natural persons during the period in "
                 "which they are in use."),
        full_text=(
            "Article 14 — Human oversight. High-risk AI systems shall be designed "
            "and developed in such a way, including with appropriate human-machine "
            "interface tools, that they can be effectively overseen by natural "
            "persons during the period in which they are in use. Oversight measures "
            "shall be commensurate with the risks, the level of autonomy and the "
            "context of use. Natural persons assigned oversight shall be able to "
            "understand the capacities and limitations of the system, monitor for "
            "anomalies, and intervene or interrupt the system through a 'stop' button."
        ),
        source_type=SourceType.LEGISLATION, source_label="EU AI Act 2024/1689",
    ),

    # --------------------------- Article 17 (quality management system)
    Reference(
        code="R-Art-17", article_no="17",
        title="Quality management system (QMS)",
        snippet=("Providers of high-risk AI systems shall put a documented quality "
                 "management system in place ensuring compliance with the Regulation."),
        full_text=(
            "Article 17 — Quality management system. Providers of high-risk AI "
            "systems shall put a quality management system in place that ensures "
            "compliance with this Regulation. That system shall be documented in a "
            "systematic and orderly manner in the form of written policies, "
            "procedures and instructions, and shall include strategies for "
            "regulatory compliance, techniques for the design, development and "
            "quality control of the system, and resource management."
        ),
        source_type=SourceType.LEGISLATION, source_label="EU AI Act 2024/1689",
    ),

    # ----------------------------------------------------- Article 27 (FRIA)
    Reference(
        code="R-Art-27", article_no="27",
        title="Fundamental rights impact assessment (FRIA)",
        snippet=("Deployers of certain high-risk AI systems shall perform an "
                 "assessment of the impact on fundamental rights that the use of "
                 "the system may produce."),
        full_text=(
            "Article 27 — Fundamental rights impact assessment for high-risk AI "
            "systems. Prior to deploying a high-risk AI system referred to in "
            "Article 6(2), with the exception of systems intended for use in "
            "critical infrastructure, deployers that are bodies governed by public "
            "law or private entities providing public services, and deployers of "
            "credit-scoring or insurance-pricing AI, shall perform an assessment of "
            "the impact on fundamental rights that the use of such a system may "
            "produce. The deployer shall notify the market surveillance authority "
            "of the results."
        ),
        source_type=SourceType.LEGISLATION, source_label="EU AI Act 2024/1689",
    ),

    # -------------------------------------- Article 50 (transparency / chatbots)
    Reference(
        code="R-Art-50", article_no="50",
        title="Transparency obligations for certain AI systems",
        snippet=("Providers and deployers of AI systems intended to interact directly "
                 "with natural persons, or that generate synthetic content, shall "
                 "ensure that users are informed."),
        full_text=(
            "Article 50 — Transparency obligations for providers and deployers of "
            "certain AI systems. Providers shall ensure that AI systems intended to "
            "interact directly with natural persons are designed and developed in "
            "such a way that the natural persons concerned are informed that they "
            "are interacting with an AI system. Providers of AI systems generating "
            "synthetic audio, image, video or text content shall ensure that the "
            "outputs are marked as artificially generated or manipulated. Deployers "
            "of deep-fake content shall disclose that the content has been "
            "artificially generated or manipulated."
        ),
        source_type=SourceType.LEGISLATION, source_label="EU AI Act 2024/1689",
    ),

    # ---------------------------------- Articles 51 / 53 / 55 (GPAI obligations)
    Reference(
        code="R-Art-51", article_no="51",
        title="Classification of GPAI models",
        snippet=("A general-purpose AI model shall be classified as having systemic "
                 "risk if it has high-impact capabilities."),
        full_text=(
            "Article 51 — Classification of general-purpose AI models as GPAI with "
            "systemic risk. A general-purpose AI model is classified as having "
            "systemic risk if it has high-impact capabilities evaluated on the basis "
            "of appropriate technical tools and methodologies, including indicators "
            "and benchmarks, or if so designated by the Commission ex officio or "
            "following a qualified alert from the scientific panel."
        ),
        source_type=SourceType.LEGISLATION, source_label="EU AI Act 2024/1689",
    ),

    Reference(
        code="R-Art-53", article_no="53",
        title="Obligations for providers of GPAI models",
        snippet=("Providers of GPAI models shall draw up and keep up-to-date "
                 "technical documentation of the model and make information "
                 "available to downstream providers."),
        full_text=(
            "Article 53 — Obligations for providers of general-purpose AI models. "
            "Providers shall draw up and keep up to date technical documentation, "
            "including training and testing process and the results of evaluation; "
            "draw up and keep up to date information for downstream providers; put "
            "in place a policy to respect Union copyright law; and publish a "
            "sufficiently detailed summary of the training content."
        ),
        source_type=SourceType.LEGISLATION, source_label="EU AI Act 2024/1689",
    ),

    Reference(
        code="R-Art-55", article_no="55",
        title="Obligations for providers of GPAI models with systemic risk",
        snippet=("Providers of GPAI models with systemic risk shall perform model "
                 "evaluation, assess and mitigate systemic risks, and report serious "
                 "incidents."),
        full_text=(
            "Article 55 — Obligations for providers of general-purpose AI models "
            "with systemic risk. In addition to obligations under Article 53, "
            "providers shall perform model evaluation including adversarial testing, "
            "assess and mitigate possible systemic risks at Union level, keep track "
            "of and report serious incidents to the AI Office, and ensure an "
            "adequate level of cybersecurity protection."
        ),
        source_type=SourceType.LEGISLATION, source_label="EU AI Act 2024/1689",
    ),

    # ---------------------------------------------- Article 71 (EU database)
    Reference(
        code="R-Art-71", article_no="71",
        title="EU database for high-risk AI systems",
        snippet=("The Commission shall set up and maintain an EU database for "
                 "high-risk AI systems referred to in Annex III; providers shall "
                 "register their systems."),
        full_text=(
            "Article 71 — EU database for high-risk AI systems listed in Annex III. "
            "The Commission shall, in collaboration with the Member States, set up "
            "and maintain a database containing information on high-risk AI systems. "
            "Providers and, where applicable, deployers that are public authorities, "
            "shall enter and update the relevant information set out in Annex VIII."
        ),
        source_type=SourceType.LEGISLATION, source_label="EU AI Act 2024/1689",
    ),

    # -------------------------------------------- Annex III §§1 / 3 / 4 / 5
    Reference(
        code="R-Annex-III-1", article_no="Annex-III-1",
        title="Annex III §1 — Biometrics",
        snippet=("AI systems intended for remote biometric identification, "
                 "biometric categorisation, or emotion recognition are considered "
                 "high-risk."),
        full_text=(
            "Annex III §1 — Biometrics. The following biometric AI systems are "
            "considered high-risk: (a) remote biometric identification systems, "
            "excluding verification confirming a specific person is the person "
            "they claim to be; (b) AI systems for biometric categorisation "
            "according to sensitive or protected attributes; (c) AI systems "
            "intended for emotion recognition outside the prohibited contexts of "
            "Article 5."
        ),
        source_type=SourceType.LEGISLATION, source_label="EU AI Act 2024/1689",
    ),

    Reference(
        code="R-Annex-III-2", article_no="Annex-III-2",
        title="Annex III §2 — Critical infrastructure",
        snippet=("AI systems intended for use as safety components in the management "
                 "and operation of critical digital infrastructure, road traffic, or "
                 "the supply of water, gas, heating, and electricity are high-risk."),
        full_text=(
            "Annex III §2 — Critical infrastructure. AI systems intended to be used "
            "as safety components in the management and operation of critical digital "
            "infrastructure, road traffic, or in the supply of water, gas, heating "
            "and electricity. Failure of such systems can endanger the life and "
            "health of persons at large scale and disrupt the ordinary conduct of "
            "social and economic activities."
        ),
        source_type=SourceType.LEGISLATION, source_label="EU AI Act 2024/1689",
    ),

    Reference(
        code="R-Annex-III-3", article_no="Annex-III-3",
        title="Annex III §3 — Education and vocational training",
        snippet=("AI systems determining access to, admission to, or assignment "
                 "within educational institutions, or evaluating learning outcomes, "
                 "are high-risk."),
        full_text=(
            "Annex III §3 — Education and vocational training. AI systems intended "
            "to be used: (a) to determine access or admission to educational and "
            "vocational training institutions or to assign natural persons to them; "
            "(b) to evaluate learning outcomes; (c) to assess the appropriate level "
            "of education for an individual; (d) to monitor and detect prohibited "
            "behaviour during tests."
        ),
        source_type=SourceType.LEGISLATION, source_label="EU AI Act 2024/1689",
    ),

    Reference(
        code="R-Annex-III-4", article_no="Annex-III-4",
        title="Annex III §4 — Employment, workers management and access to self-employment",
        snippet=("AI systems for recruitment or selection of natural persons — in "
                 "particular advertising, filtering applications and evaluating "
                 "candidates — are high-risk."),
        full_text=(
            "Annex III §4 — Employment, workers management and access to "
            "self-employment. AI systems intended to be used: (a) for the "
            "recruitment or selection of natural persons, in particular to place "
            "targeted job advertisements, to analyse and filter job applications, "
            "and to evaluate candidates; (b) to make decisions affecting terms of "
            "work-related relationships, the promotion or termination of "
            "work-related contractual relationships, to allocate tasks based on "
            "individual behaviour or personal traits or characteristics, or to "
            "monitor and evaluate the performance and behaviour of persons."
        ),
        source_type=SourceType.LEGISLATION, source_label="EU AI Act 2024/1689",
    ),

    Reference(
        code="R-Annex-III-5", article_no="Annex-III-5",
        title="Annex III §5 — Essential private and public services",
        snippet=("AI systems used to evaluate eligibility for essential services or "
                 "benefits, including credit-worthiness of natural persons, are "
                 "high-risk."),
        full_text=(
            "Annex III §5 — Access to and enjoyment of essential private services "
            "and essential public services and benefits. AI systems intended to be "
            "used: (a) by public authorities to evaluate the eligibility of natural "
            "persons for benefits and services; (b) to evaluate the creditworthiness "
            "of natural persons or establish credit scores, with the exception of "
            "AI used for the purpose of detecting financial fraud; (c) for risk "
            "assessment and pricing in life and health insurance; (d) to evaluate "
            "and classify emergency calls or to dispatch emergency services."
        ),
        source_type=SourceType.LEGISLATION, source_label="EU AI Act 2024/1689",
    ),

    Reference(
        code="R-Annex-III-6", article_no="Annex-III-6",
        title="Annex III §6 — Law enforcement",
        snippet=("AI systems intended to be used by law enforcement authorities for "
                 "risk profiling, evidence evaluation, polygraphs, or crime analytics "
                 "are high-risk."),
        full_text=(
            "Annex III §6 — Law enforcement. AI systems intended to be used by, or on "
            "behalf of, law enforcement authorities, or by Union institutions, bodies, "
            "offices, or agencies in support of law enforcement, for: (a) assessing "
            "the risk of a natural person becoming the victim of criminal offences; "
            "(b) polygraphs and similar tools; (c) evaluating the reliability of "
            "evidence; (d) profiling natural persons in the course of detection, "
            "investigation, or prosecution of criminal offences; (e) crime analytics."
        ),
        source_type=SourceType.LEGISLATION, source_label="EU AI Act 2024/1689",
    ),

    Reference(
        code="R-Annex-III-7", article_no="Annex-III-7",
        title="Annex III §7 — Migration, asylum, and border control",
        snippet=("AI systems used by competent authorities for migration, asylum, or "
                 "border-control management — including risk assessments and document "
                 "verification — are high-risk."),
        full_text=(
            "Annex III §7 — Migration, asylum, and border control management. AI "
            "systems intended to be used by competent public authorities, or by Union "
            "institutions, bodies, offices, or agencies, for: (a) polygraphs and "
            "similar tools; (b) assessing security, irregular-migration, or health "
            "risks posed by a natural person who intends to enter the Union; (c) "
            "examining applications for asylum, visas, and residence permits and "
            "associated complaints; (d) detecting, recognising, or identifying natural "
            "persons in border-management contexts."
        ),
        source_type=SourceType.LEGISLATION, source_label="EU AI Act 2024/1689",
    ),

    Reference(
        code="R-Annex-III-8", article_no="Annex-III-8",
        title="Annex III §8 — Administration of justice and democratic processes",
        snippet=("AI systems assisting judicial authorities in researching or "
                 "interpreting facts and law, or used to influence elections or "
                 "voting behaviour, are high-risk."),
        full_text=(
            "Annex III §8 — Administration of justice and democratic processes. AI "
            "systems intended to be used: (a) by a judicial authority, or on its "
            "behalf, to assist in researching and interpreting facts and the law and "
            "in applying the law to a concrete set of facts, or in alternative "
            "dispute resolution; (b) to influence the outcome of an election or "
            "referendum or the voting behaviour of natural persons, with the "
            "exception of outputs whose addressee is not directly exposed to the "
            "system (such as back-office logistical tools)."
        ),
        source_type=SourceType.LEGISLATION, source_label="EU AI Act 2024/1689",
    ),

    # -------------------------------------------------------------- Recitals
    Reference(
        code="R-Recital-31", article_no="Recital-31",
        title="Recital 31 — Social scoring concerns",
        snippet=("AI systems providing social scoring of natural persons can lead "
                 "to discriminatory outcomes and exclusion."),
        full_text=(
            "Recital 31 — AI systems providing social scoring of natural persons by "
            "public or private actors may lead to discriminatory outcomes and the "
            "exclusion of certain groups. They may violate the right to dignity and "
            "non-discrimination and values of equality and justice. Such systems "
            "are therefore prohibited under Article 5."
        ),
        source_type=SourceType.LEGISLATION, source_label="EU AI Act 2024/1689",
    ),

    Reference(
        code="R-Recital-44", article_no="Recital-44",
        title="Recital 44 — Emotion recognition risks",
        snippet=("Emotion-recognition AI in workplace and education raises serious "
                 "concerns about scientific basis, bias, and intrusion."),
        full_text=(
            "Recital 44 — Serious concerns exist about the scientific basis of AI "
            "systems aimed at identifying or inferring emotions, particularly in "
            "the workplace and in education, where there is a power imbalance. "
            "Such systems can lead to detrimental or unfavourable treatment and are "
            "prohibited in those contexts."
        ),
        source_type=SourceType.LEGISLATION, source_label="EU AI Act 2024/1689",
    ),

    Reference(
        code="R-Recital-53", article_no="Recital-53",
        title="Recital 53 — Minimal-risk systems",
        snippet=("The vast majority of AI systems currently used pose minimal or no "
                 "risk and may contribute to important benefits."),
        full_text=(
            "Recital 53 — The vast majority of AI systems currently used in the "
            "Union pose minimal or no risk and may contribute to important societal "
            "and economic benefits. They are not subject to specific obligations "
            "under this Regulation, but providers and deployers are encouraged to "
            "apply voluntary codes of conduct."
        ),
        source_type=SourceType.LEGISLATION, source_label="EU AI Act 2024/1689",
    ),

    Reference(
        code="R-Recital-71", article_no="Recital-71",
        title="Recital 71 — High-risk classification rationale",
        snippet=("AI systems should be classified as high-risk only when they pose "
                 "significant risk of harm to fundamental rights, health, or safety."),
        full_text=(
            "Recital 71 — AI systems should be classified as high-risk only when "
            "they pose a significant risk of harm to the health, safety or "
            "fundamental rights of natural persons, taking into account the "
            "severity of the possible harm and its probability of occurrence."
        ),
        source_type=SourceType.LEGISLATION, source_label="EU AI Act 2024/1689",
    ),

    Reference(
        code="R-Recital-132", article_no="Recital-132",
        title="Recital 132 — Transparency for AI interactions",
        snippet=("Natural persons should be informed when they are interacting with "
                 "an AI system, unless this is obvious from the circumstances."),
        full_text=(
            "Recital 132 — Natural persons should be informed when they are "
            "interacting with an AI system, unless that is obvious from the "
            "circumstances and the context of use. The obligation to inform should "
            "be considered fulfilled when the AI system is clearly identifiable as "
            "such, taking into account the perception of an averagely well-informed "
            "and observant person."
        ),
        source_type=SourceType.LEGISLATION, source_label="EU AI Act 2024/1689",
    ),

    Reference(
        code="R-Recital-134", article_no="Recital-134",
        title="Recital 134 — Synthetic content disclosure",
        snippet=("Providers of generative AI should mark outputs in a machine-readable "
                 "format detectable as artificially generated."),
        full_text=(
            "Recital 134 — Providers of AI systems generating synthetic audio, "
            "image, video or text should ensure that outputs are marked in a "
            "machine-readable format and detectable as artificially generated or "
            "manipulated. Technical solutions should be effective, interoperable, "
            "robust and reliable, taking into account the state of the art."
        ),
        source_type=SourceType.LEGISLATION, source_label="EU AI Act 2024/1689",
    ),

    # ----------------------------------------- Guidance (Commission, EUR-Lex)
    Reference(
        code="R-Guide-prohibited-001", article_no="Guide-prohibited-001",
        title="Commission guidance on prohibited AI practices",
        snippet=("Guidance clarifying scope of Article 5 prohibitions, including "
                 "the workplace emotion-recognition prohibition."),
        full_text=(
            "Commission guidance on prohibited AI practices (Article 5). The "
            "guidance clarifies that emotion-recognition systems used in the "
            "workplace fall under the prohibition irrespective of whether they "
            "are used by the employer or by a third party on the employer's "
            "behalf. Medical and safety-related uses are out of scope of the "
            "prohibition."
        ),
        source_type=SourceType.GUIDANCE, source_label="European Commission, AI Office",
    ),

    # ----------------------------------------- Finnish national implementation
    Reference(
        code="R-FI-traficom-001", article_no="FI-Traficom-001",
        title="Finnish national competent authority (Traficom)",
        snippet=("Traficom is the designated Finnish notifying authority and market "
                 "surveillance authority under the AI Act."),
        full_text=(
            "Finland has designated Liikenne- ja viestintävirasto (Traficom) as the "
            "national notifying authority and market surveillance authority for the "
            "AI Act. Deployers and providers established in Finland should direct "
            "incident reports, FRIA notifications, and registration queries to "
            "Traficom's AI Office unit."
        ),
        source_type=SourceType.NATIONAL,
        source_label="Traficom (Finland)",
    ),
]


def get_all() -> list[Reference]:
    return SEED_CHUNKS


def by_code(code: str):
    for c in SEED_CHUNKS:
        if c.code == code:
            return c
    return None
