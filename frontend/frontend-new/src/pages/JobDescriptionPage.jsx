import { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Briefcase,
  Building2,
  CheckCircle,
  ChevronDown,
  ClipboardList,
  FileText,
  Loader2,
  MapPin,
  Plus,
  RotateCcw,
  Send,
  Sparkles,
  Trash2,
  Wand2,
  X,
} from 'lucide-react'
import { CardSkeleton } from '../components/LoadingSkeleton'
import ErrorState from '../components/ErrorState'
import api from '../services/api'

const EMPTY_FORM = {
  role: '',
  company: '',
  location: '',
  experience: '',
  responsibilities: [''],
  must_have_skills: [],
  nice_to_have_skills: [],
}

const SAMPLE_JDS = [
  {
    label: 'Senior Machine Learning Engineer',
    value: {
      role: 'Senior Machine Learning Engineer',
      company: 'TechCorp AI',
      location: 'San Francisco, CA / Remote',
      experience: '5-8 years',
      responsibilities: [
        'Own model training, evaluation, deployment, and monitoring for production ML systems.',
        'Partner with product and data teams to translate requirements into reliable ML services.',
        'Improve experimentation, feature engineering, and model release workflows.',
      ],
      must_have_skills: ['Python', 'PyTorch', 'TensorFlow', 'ML model deployment', 'MLOps'],
      nice_to_have_skills: ['Kubernetes', 'Spark', 'A/B testing'],
    },
  },
  {
    label: 'Applied AI Engineer',
    value: {
      role: 'Applied AI Engineer',
      company: 'InnovateLabs',
      location: 'New York, NY',
      experience: '4-7 years',
      responsibilities: [
        'Build AI product features using retrieval, ranking, embeddings, and production APIs.',
        'Design evaluation loops for model quality, latency, reliability, and user outcomes.',
        'Work with engineering teams to ship AI workflows into customer-facing systems.',
      ],
      must_have_skills: ['Python', 'RAG pipelines', 'Vector databases', 'LLM integration', 'Prompt engineering'],
      nice_to_have_skills: ['LangChain', 'FastAPI', 'AWS', 'GCP'],
    },
  },
  {
    label: 'LLM Engineer',
    value: {
      role: 'LLM Engineer',
      company: 'FoundationAI',
      location: 'London, UK / Remote',
      experience: '3-6 years',
      responsibilities: [
        'Develop LLM applications with retrieval, fine-tuning, inference, and evaluation workflows.',
        'Improve model quality through prompt design, datasets, LoRA experiments, and offline metrics.',
        'Deploy scalable LLM services with monitoring, safety checks, and latency controls.',
      ],
      must_have_skills: ['Large language models', 'RAG', 'Fine-tuning', 'LoRA', 'Python'],
      nice_to_have_skills: ['vLLM', 'TGI', 'Distributed training', 'RLHF'],
    },
  },
  {
    label: 'NLP Engineer',
    value: {
      role: 'NLP Engineer',
      company: 'DataMinds',
      location: 'Bangalore, India',
      experience: '3-6 years',
      responsibilities: [
        'Build NLP systems for classification, extraction, search, and language understanding.',
        'Train and evaluate transformer-based models for text products and internal platforms.',
        'Create robust preprocessing, annotation, and model monitoring workflows.',
      ],
      must_have_skills: ['NLP', 'Hugging Face Transformers', 'Python', 'Text classification', 'NER'],
      nice_to_have_skills: ['spaCy', 'Elasticsearch', 'Multilingual models'],
    },
  },
  {
    label: 'Data Scientist',
    value: {
      role: 'Data Scientist',
      company: 'AnalyticsPro',
      location: 'Austin, TX / Hybrid',
      experience: '3-5 years',
      responsibilities: [
        'Build statistical and machine learning models to solve business and product problems.',
        'Partner with stakeholders on experiment design, metrics, dashboarding, and analysis.',
        'Translate data findings into clear recommendations and production-ready features.',
      ],
      must_have_skills: ['Python', 'SQL', 'Statistical modeling', 'Machine Learning', 'Data visualization'],
      nice_to_have_skills: ['Deep learning', 'Tableau', 'Power BI', 'Experiment design'],
    },
  },
]

const COMMON_SKILLS = [
  'Python', 'SQL', 'Machine Learning', 'Deep Learning', 'NLP', 'RAG', 'LangChain',
  'Vector databases', 'Embeddings', 'Hugging Face', 'Spark', 'MLOps',
  'Kubernetes', 'PyTorch', 'TensorFlow', 'Fine-tuning', 'LoRA', 'FastAPI',
]

const cloneForm = (form) => ({
  ...form,
  responsibilities: [...(form.responsibilities || [''])],
  must_have_skills: [...(form.must_have_skills || [])],
  nice_to_have_skills: [...(form.nice_to_have_skills || [])],
})

const splitList = (value) =>
  (value || '')
    .split(/[,;\n]/)
    .map((item) => item.replace(/^[-*]\s*/, '').trim())
    .filter(Boolean)

const unique = (items) => [...new Set(items.map((item) => item.trim()).filter(Boolean))]

const extractLine = (text, labels) => {
  const escaped = labels.map((label) => label.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')
  const match = text.match(new RegExp(`(?:^|\\n)\\s*(?:${escaped})\\s*[:\\-]\\s*(.+)`, 'i'))
  return match?.[1]?.trim() || ''
}

const extractExperience = (text) => {
  const labeled = extractLine(text, ['experience', 'years', 'seniority'])
  if (labeled) return labeled
  const range = text.match(/(\d+\s*[-+]\s*\d+\s*(?:years|yrs|y))/i)
  if (range) return range[1].replace(/\s+/g, ' ')
  const single = text.match(/(\d+\+?\s*(?:years|yrs|y)(?:\s+of\s+experience)?)/i)
  return single?.[1]?.replace(/\s+/g, ' ') || ''
}

const extractRole = (text) => {
  const labeled = extractLine(text, ['role', 'title', 'position', 'job title'])
  if (labeled) return labeled
  const hiring = text.match(/(?:hiring|seeking|looking for)\s+(?:an?\s+)?([A-Z][A-Za-z0-9 /+-]*(?:Engineer|Scientist|Analyst|Manager|Lead|Architect|Developer|Specialist))/)
  return hiring?.[1]?.trim() || ''
}

const extractBulletsAfter = (text, headings) => {
  const lines = text.split('\n')
  const headingIndex = lines.findIndex((line) =>
    headings.some((heading) => line.toLowerCase().includes(heading))
  )
  if (headingIndex < 0) return []
  const items = []
  for (let i = headingIndex + 1; i < lines.length; i += 1) {
    const line = lines[i].trim()
    if (!line) {
      if (items.length) break
      continue
    }
    if (/^[A-Za-z][A-Za-z ]{2,}:$/.test(line) && items.length) break
    if (/^[-*]/.test(line) || /^\d+[.)]/.test(line)) {
      items.push(line.replace(/^[-*\d.)\s]+/, '').trim())
    } else if (items.length) {
      break
    }
  }
  return items.filter(Boolean)
}

const extractSkills = (text, labels, fallbackNeedles = []) => {
  const labeled = labels.flatMap((label) => splitList(extractLine(text, [label])))
  const bullets = extractBulletsAfter(text, labels.map((label) => label.toLowerCase()))
  const normalizedText = text.toLowerCase()
  const detected = COMMON_SKILLS.filter((skill) => normalizedText.includes(skill.toLowerCase()))
  const fallback = fallbackNeedles.filter((skill) => normalizedText.includes(skill.toLowerCase()))
  return unique([...labeled, ...bullets, ...detected, ...fallback]).slice(0, 12)
}

const parseFreeTextJD = (text) => {
  const responsibilities = extractBulletsAfter(text, ['responsibilities', 'what you will do', 'you will', 'scope'])
  return {
    role: extractRole(text),
    company: extractLine(text, ['company', 'team']),
    location: extractLine(text, ['location', 'work location']),
    experience: extractExperience(text),
    responsibilities: responsibilities.length ? responsibilities : splitList(extractLine(text, ['responsibilities'])).slice(0, 6),
    must_have_skills: extractSkills(text, ['must-have skills', 'must have', 'requirements', 'required skills']),
    nice_to_have_skills: extractSkills(text, ['nice-to-have skills', 'nice to have', 'preferred skills', 'bonus skills']),
  }
}

const buildPayload = (form, customRole, freeText) => {
  const parsed = freeText.trim() ? parseFreeTextJD(freeText) : {}
  const merged = {
    role: customRole.trim() || parsed.role || form.role,
    company: parsed.company || form.company,
    location: parsed.location || form.location,
    experience: parsed.experience || form.experience,
    responsibilities: parsed.responsibilities?.length ? parsed.responsibilities : form.responsibilities.filter(Boolean),
    must_have_skills: parsed.must_have_skills?.length ? parsed.must_have_skills : form.must_have_skills,
    nice_to_have_skills: parsed.nice_to_have_skills?.length ? parsed.nice_to_have_skills : form.nice_to_have_skills,
    job_description: freeText.trim() || [
      ...form.responsibilities.filter(Boolean),
      ...form.must_have_skills.map((skill) => `Must have: ${skill}`),
      ...form.nice_to_have_skills.map((skill) => `Nice to have: ${skill}`),
    ].join('\n'),
  }
  return {
    ...merged,
    role: merged.role || 'Custom Role',
    responsibilities: merged.responsibilities || [],
    must_have_skills: unique(merged.must_have_skills || []),
    nice_to_have_skills: unique(merged.nice_to_have_skills || []),
  }
}

function ChipEditor({ label, values, onChange, placeholder, variant = 'brand' }) {
  const [draft, setDraft] = useState('')

  const addChip = () => {
    const additions = splitList(draft)
    if (!additions.length) return
    onChange(unique([...values, ...additions]))
    setDraft('')
  }

  return (
    <div className="ats-field ats-field-wide">
      <label>{label}</label>
      <div className="ats-chip-box">
        {values.map((value) => (
          <button
            key={value}
            className={`ats-skill-chip ats-skill-chip-${variant}`}
            type="button"
            onClick={() => onChange(values.filter((item) => item !== value))}
            title="Remove skill"
          >
            {value}
            <X size={13} />
          </button>
        ))}
        <input
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter' || event.key === ',') {
              event.preventDefault()
              addChip()
            }
          }}
          onBlur={addChip}
          placeholder={placeholder}
        />
      </div>
    </div>
  )
}

export default function JobDescriptionPage({ showToast }) {
  const [currentJd, setCurrentJd] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [form, setForm] = useState(cloneForm(EMPTY_FORM))
  const [customRole, setCustomRole] = useState('')
  const [freeText, setFreeText] = useState('')
  const [selectedSample, setSelectedSample] = useState('')
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [extracted, setExtracted] = useState(null)
  const [analyzeSuccess, setAnalyzeSuccess] = useState(false)
  const dropdownRef = useRef(null)
  const navigate = useNavigate()

  const fetchJD = () => {
    setLoading(true)
    setError(null)
    api
      .get('/jd')
      .then((res) => {
        setCurrentJd(res.data)
        setForm(cloneForm({
          ...EMPTY_FORM,
          ...res.data,
          responsibilities: res.data.responsibilities || EMPTY_FORM.responsibilities,
          must_have_skills: res.data.must_have_skills || [],
          nice_to_have_skills: res.data.nice_to_have_skills || [],
        }))
      })
      .catch((err) => setError(err.response?.data?.detail || err.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchJD()
  }, [])

  useEffect(() => {
    const handleClick = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  const payloadPreview = useMemo(
    () => buildPayload(form, customRole, freeText),
    [form, customRole, freeText]
  )

  const setField = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }))
    setAnalyzeSuccess(false)
  }

  const handleSelectSample = (sample) => {
    setSelectedSample(sample.label)
    setForm(cloneForm(sample.value))
    setCustomRole('')
    setFreeText('')
    setExtracted(null)
    setAnalyzeSuccess(false)
    setDropdownOpen(false)
  }

  const handleResponsibilityChange = (index, value) => {
    const next = [...form.responsibilities]
    next[index] = value
    setField('responsibilities', next)
  }

  const addResponsibility = () => {
    setField('responsibilities', [...form.responsibilities, ''])
  }

  const removeResponsibility = (index) => {
    const next = form.responsibilities.filter((_, itemIndex) => itemIndex !== index)
    setField('responsibilities', next.length ? next : [''])
  }

  const handleClear = () => {
    setForm(cloneForm(EMPTY_FORM))
    setCustomRole('')
    setFreeText('')
    setSelectedSample('')
    setExtracted(null)
    setAnalyzeSuccess(false)
  }

  const handleAnalyze = async () => {
    const payload = buildPayload(form, customRole, freeText)
    const jdString = JSON.stringify(payload)
    if (analyzing || jdString.length < 20) return

    setAnalyzing(true)
    setAnalyzeSuccess(false)
    setExtracted(payload)
    localStorage.setItem('currentJD', jdString)

    try {
      await api.get('/rank', {
        params: { jd: jdString, page: 1, limit: 1 },
      })
      setAnalyzeSuccess(true)
      showToast?.('Requirements extracted and candidates analyzed.')
    } catch (err) {
      console.error('Analyze failed:', err)
      showToast?.('Analysis failed. Please check the job description.', 'error')
    } finally {
      setAnalyzing(false)
    }
  }

  if (loading) return <CardSkeleton count={2} />
  if (error) return <ErrorState message={error} onRetry={fetchJD} />

  return (
    <div className="page-container ats-jd-page">
      <motion.div className="ats-page-header" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}>
        <div>
          <h1 className="page-title">Job Description</h1>
          <p className="page-subtitle">
            Build a recruiter-ready role profile. Samples are editable, custom role titles override samples, and pasted JDs are converted into the backend JSON payload automatically.
          </p>
        </div>
        <button className="btn btn-secondary" type="button" onClick={handleClear}>
          <RotateCcw size={16} />
          Reset
        </button>
      </motion.div>

      <div className="ats-jd-layout">
        <motion.section className="card ats-workspace" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
          <div className="ats-section-heading">
            <div>
              <span className="ats-eyebrow">Role setup</span>
              <h2>Recruiter intake form</h2>
            </div>
            <span className="badge badge-info">No JSON required</span>
          </div>

          <div className="ats-field ats-field-wide" ref={dropdownRef}>
            <label>Predefined sample roles</label>
            <button className="ats-select" type="button" onClick={() => setDropdownOpen((open) => !open)}>
              <span>{selectedSample || 'Choose a sample role'}</span>
              <ChevronDown size={16} className={dropdownOpen ? 'ats-rotate' : ''} />
            </button>
            {dropdownOpen && (
              <div className="ats-select-menu">
                {SAMPLE_JDS.map((sample) => (
                  <button
                    key={sample.label}
                    type="button"
                    className={selectedSample === sample.label ? 'active' : ''}
                    onClick={() => handleSelectSample(sample)}
                  >
                    {sample.label}
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="ats-form-grid">
            <div className="ats-field">
              <label>Role</label>
              <input value={form.role} onChange={(event) => setField('role', event.target.value)} placeholder="Role title" />
            </div>
            <div className="ats-field">
              <label>Custom Role Override</label>
              <input value={customRole} onChange={(event) => setCustomRole(event.target.value)} placeholder="Overrides selected sample" />
            </div>
            <div className="ats-field">
              <label>Company</label>
              <input value={form.company} onChange={(event) => setField('company', event.target.value)} placeholder="Company name" />
            </div>
            <div className="ats-field">
              <label>Location</label>
              <input value={form.location} onChange={(event) => setField('location', event.target.value)} placeholder="City, remote, hybrid" />
            </div>
            <div className="ats-field">
              <label>Experience</label>
              <input value={form.experience} onChange={(event) => setField('experience', event.target.value)} placeholder="5-8 years" />
            </div>
          </div>

          <div className="ats-field ats-field-wide">
            <label>Responsibilities</label>
            <div className="ats-bullet-list">
              {form.responsibilities.map((item, index) => (
                <div className="ats-bullet-row" key={index}>
                  <span>{index + 1}</span>
                  <input
                    value={item}
                    onChange={(event) => handleResponsibilityChange(index, event.target.value)}
                    placeholder="Add a responsibility"
                  />
                  <button type="button" onClick={() => removeResponsibility(index)} aria-label="Remove responsibility">
                    <Trash2 size={15} />
                  </button>
                </div>
              ))}
            </div>
            <button className="btn btn-secondary btn-sm" type="button" onClick={addResponsibility}>
              <Plus size={14} />
              Add responsibility
            </button>
          </div>

          <ChipEditor
            label="Must-have Skills"
            values={form.must_have_skills}
            onChange={(values) => setField('must_have_skills', values)}
            placeholder="Type skill and press Enter"
            variant="brand"
          />
          <ChipEditor
            label="Nice-to-have Skills"
            values={form.nice_to_have_skills}
            onChange={(values) => setField('nice_to_have_skills', values)}
            placeholder="Type skill and press Enter"
            variant="muted"
          />

          <div className="ats-field ats-field-wide">
            <label>Paste or Write Your Own Job Description</label>
            <textarea
              className="ats-free-text"
              value={freeText}
              onChange={(event) => {
                setFreeText(event.target.value)
                setAnalyzeSuccess(false)
              }}
              placeholder="Paste a normal English job description here. We will extract the role, company, location, experience range, responsibilities, and skills automatically."
            />
          </div>

          <div className="ats-action-bar">
            <button className="btn btn-primary ats-analyze-btn" type="button" disabled={analyzing} onClick={handleAnalyze}>
              {analyzing ? (
                <>
                  <Loader2 className="jd-spinner" size={18} />
                  Analyzing Candidates
                </>
              ) : analyzeSuccess ? (
                <>
                  <CheckCircle size={18} />
                  Analysis Complete
                </>
              ) : (
                <>
                  <Send size={18} />
                  Analyze Candidates
                </>
              )}
            </button>
            {analyzeSuccess && (
              <button className="btn btn-secondary" type="button" onClick={() => navigate('/rankings')}>
                View Rankings
              </button>
            )}
          </div>
        </motion.section>

        <aside className="ats-side-panel">
          <motion.section className="card ats-summary-card" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}>
            <span className="ats-eyebrow">Active role</span>
            <h2>{customRole.trim() || form.role || currentJd?.role || 'Untitled role'}</h2>
            <div className="ats-meta-list">
              <span><Building2 size={15} /> {form.company || currentJd?.company || 'Company pending'}</span>
              <span><MapPin size={15} /> {form.location || currentJd?.location || 'Location pending'}</span>
              <span><Briefcase size={15} /> {form.experience || currentJd?.experience || 'Experience pending'}</span>
            </div>
          </motion.section>

          <motion.section className="card ats-summary-card" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <div className="ats-section-heading compact">
              <div>
                <span className="ats-eyebrow">AI extracted requirements</span>
                <h2>{extracted ? 'Ready for ranking' : 'Preview'}</h2>
              </div>
              <Wand2 size={18} />
            </div>
            <div className="ats-extracted-block">
              <h3><FileText size={15} /> Responsibilities</h3>
              <ul>
                {(extracted || payloadPreview).responsibilities.slice(0, 4).map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
            <div className="ats-extracted-block">
              <h3><ClipboardList size={15} /> Must-have</h3>
              <div className="ats-preview-chips">
                {(extracted || payloadPreview).must_have_skills.map((skill) => (
                  <span key={skill} className="ats-skill-chip ats-skill-chip-brand">{skill}</span>
                ))}
              </div>
            </div>
            <div className="ats-extracted-block">
              <h3><Sparkles size={15} /> Nice-to-have</h3>
              <div className="ats-preview-chips">
                {(extracted || payloadPreview).nice_to_have_skills.map((skill) => (
                  <span key={skill} className="ats-skill-chip ats-skill-chip-muted">{skill}</span>
                ))}
              </div>
            </div>
          </motion.section>
        </aside>
      </div>
    </div>
  )
}
