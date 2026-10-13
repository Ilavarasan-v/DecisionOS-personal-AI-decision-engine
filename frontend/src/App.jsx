import { useEffect, useRef, useState } from 'react'

import {
  getUserDecisions,
  getUserPreferences,
  createDecision,
  evaluateDecision,
  submitFeedback,
  learnFromFeedback,
  getUserLearningHistory,
  getUserFeedback,
} from './services/api'

import './App.css'
import './Feedback.css'

function App() {
  const [decisions, setDecisions] = useState([])
  const [preferences, setPreferences] = useState([])

  const [loadingDecisions, setLoadingDecisions] = useState(true)
  const [loadingPreferences, setLoadingPreferences] = useState(true)

  const [decisionError, setDecisionError] = useState('')
  const [preferenceError, setPreferenceError] = useState('')

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [creatingDecision, setCreatingDecision] = useState(false)
  const [createDecisionError, setCreateDecisionError] = useState('')

  const [evaluatingDecisionId, setEvaluatingDecisionId] = useState(null)
  const [evaluationResult, setEvaluationResult] = useState(null)
  const [evaluationError, setEvaluationError] = useState('')

  const [feedbackDecisionId, setFeedbackDecisionId] = useState(null)
  const [feedbackOptionId, setFeedbackOptionId] = useState('')
  const [feedbackRating, setFeedbackRating] = useState(5)
  const [feedbackNotes, setFeedbackNotes] = useState('')
  const [criterionRatings, setCriterionRatings] = useState({})
  const [submittingFeedback, setSubmittingFeedback] = useState(false)
  const [feedbackError, setFeedbackError] = useState('')
  const [feedbackMessage, setFeedbackMessage] = useState('')
  const [feedbackSubmittedDecisionIds, setFeedbackSubmittedDecisionIds] = useState(
    () => new Set(),
  )
  const feedbackSubmitLock = useRef(new Set())

  const [learningHistory, setLearningHistory] = useState([])
  const [loadingLearningHistory, setLoadingLearningHistory] = useState(true)
  const [learningHistoryError, setLearningHistoryError] = useState('')
  const [activeNavItem, setActiveNavItem] = useState('dashboard')

  const [feedbackRecords, setFeedbackRecords] = useState([])
  const [loadingFeedbackRecords, setLoadingFeedbackRecords] = useState(true)
  const [feedbackRecordsError, setFeedbackRecordsError] = useState('')

  const [newDecision, setNewDecision] = useState({
    title: '',
    description: '',
    options: [
      {
        name: '',
        description: '',
        attributes: {},
      },
      {
        name: '',
        description: '',
        attributes: {},
      },
    ],
  })

  const userId = import.meta.env.VITE_USER_ID

  const refreshLearningHistory = async () => {
    if (!userId) {
      setLearningHistory([])
      setLearningHistoryError('VITE_USER_ID is not configured.')
      setLoadingLearningHistory(false)
      return
    }

    try {
      setLoadingLearningHistory(true)
      setLearningHistoryError('')
      const data = await getUserLearningHistory(userId)
      setLearningHistory(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Failed to load learning history:', error)
      setLearningHistoryError(
        error.response?.data?.detail ||
        'Unable to load your learning history.',
      )
    } finally {
      setLoadingLearningHistory(false)
    }
  }

  const refreshFeedbackRecords = async () => {
    if (!userId) {
      setFeedbackRecords([])
      setFeedbackRecordsError('VITE_USER_ID is not configured.')
      setLoadingFeedbackRecords(false)
      return
    }

    try {
      setLoadingFeedbackRecords(true)
      setFeedbackRecordsError('')
      const data = await getUserFeedback(userId)
      setFeedbackRecords(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Failed to load feedback analytics:', error)
      setFeedbackRecordsError(
        error.response?.data?.detail ||
        'Unable to load your feedback analytics.',
      )
    } finally {
      setLoadingFeedbackRecords(false)
    }
  }

  const navigateToSection = (navItem, sectionId) => {
    setActiveNavItem(navItem)
    document.getElementById(sectionId)?.scrollIntoView({
      behavior: 'smooth',
      block: 'start',
    })
  }

  useEffect(() => {
    const loadDecisions = async () => {
      try {
        setLoadingDecisions(true)
        setDecisionError('')

        const data = await getUserDecisions(userId)

        setDecisions(data)
      } catch (error) {
        console.error('Failed to load decisions:', error)

        setDecisionError(
          error.response?.data?.detail ||
          'Unable to connect to the DecisionOS backend.',
        )
      } finally {
        setLoadingDecisions(false)
      }
    }

    const loadPreferences = async () => {
      try {
        setLoadingPreferences(true)
        setPreferenceError('')

        const data = await getUserPreferences(userId)

        setPreferences(data)
      } catch (error) {
        console.error('Failed to load preferences:', error)

        setPreferenceError(
          error.response?.data?.detail ||
          'Unable to load your preference profile.',
        )
      } finally {
        setLoadingPreferences(false)
      }
    }

    if (userId) {
      loadDecisions()
      loadPreferences()
      refreshLearningHistory()
      refreshFeedbackRecords()
    } else {
      setLoadingDecisions(false)
      setLoadingPreferences(false)
      setLoadingLearningHistory(false)
      setLoadingFeedbackRecords(false)

      setDecisionError('VITE_USER_ID is not configured.')
      setPreferenceError('VITE_USER_ID is not configured.')
      setLearningHistoryError('VITE_USER_ID is not configured.')
      setFeedbackRecordsError('VITE_USER_ID is not configured.')
    }
  }, [userId])

  const openCreateDecisionModal = () => {
    setCreateDecisionError('')

    setNewDecision({
      title: '',
      description: '',
      options: [
        {
          name: '',
          description: '',
          attributes: {},
        },
        {
          name: '',
          description: '',
          attributes: {},
        },
      ],
    })

    setIsCreateModalOpen(true)
  }

  const closeCreateDecisionModal = () => {
    if (creatingDecision) {
      return
    }

    setIsCreateModalOpen(false)
    setCreateDecisionError('')
  }

  const handleDecisionFieldChange = (field, value) => {
    setNewDecision((current) => ({
      ...current,
      [field]: value,
    }))
  }

  const handleOptionFieldChange = (
    optionIndex,
    field,
    value,
  ) => {
    setNewDecision((current) => ({
      ...current,
      options: current.options.map((option, index) =>
        index === optionIndex
          ? {
            ...option,
            [field]: value,
          }
          : option,
      ),
    }))
  }

  const handleOptionAttributeChange = (
    optionIndex,
    criterion,
    value,
  ) => {
    setNewDecision((current) => ({
      ...current,
      options: current.options.map((option, index) => {
        if (index !== optionIndex) {
          return option
        }

        return {
          ...option,
          attributes: {
            ...option.attributes,
            [criterion]: value,
          },
        }
      }),
    }))
  }

  const addOption = () => {
    setNewDecision((current) => ({
      ...current,
      options: [
        ...current.options,
        {
          name: '',
          description: '',
          attributes: {},
        },
      ],
    }))
  }

  const removeOption = (optionIndex) => {
    setNewDecision((current) => ({
      ...current,
      options: current.options.filter(
        (_, index) => index !== optionIndex,
      ),
    }))
  }

  const handleCreateDecision = async (event) => {
    event.preventDefault()

    setCreateDecisionError('')

    const title = newDecision.title.trim()

    if (!title) {
      setCreateDecisionError(
        'Please enter a title for the decision.',
      )
      return
    }

    if (newDecision.options.length < 2) {
      setCreateDecisionError(
        'A decision needs at least two options.',
      )
      return
    }

    const hasEmptyOption = newDecision.options.some(
      (option) => !option.name.trim(),
    )

    if (hasEmptyOption) {
      setCreateDecisionError(
        'Please enter a name for every option.',
      )
      return
    }

    const hasInvalidAttribute = newDecision.options.some(
      (option) =>
        Object.values(option.attributes).some(
          (value) =>
            value === '' ||
            value === null ||
            Number.isNaN(Number(value)),
        ),
    )

    if (hasInvalidAttribute) {
      setCreateDecisionError(
        'Please enter valid numeric values for all preference criteria.',
      )
      return
    }

    const payload = {
      user_id: userId,
      title,
      description:
        newDecision.description.trim() || null,
      options: newDecision.options.map((option) => ({
        name: option.name.trim(),
        description:
          option.description.trim() || null,
        attributes: Object.fromEntries(
          Object.entries(option.attributes).map(
            ([criterion, value]) => [
              criterion,
              Number(value),
            ],
          ),
        ),
      })),
    }

    try {
      setCreatingDecision(true)

      const createdDecision =
        await createDecision(payload)

      setDecisions((current) => [
        createdDecision,
        ...current,
      ])

      setIsCreateModalOpen(false)
      setCreateDecisionError('')
    } catch (error) {
      console.error(
        'Failed to create decision:',
        error,
      )

      setCreateDecisionError(
        error.response?.data?.detail ||
        'Unable to create the decision. Please try again.',
      )
    } finally {
      setCreatingDecision(false)
    }
  }

  const handleEvaluateDecision = async (decisionId) => {
    try {
      setEvaluatingDecisionId(decisionId)
      setEvaluationError('')
      setEvaluationResult(null)

      const result = await evaluateDecision(decisionId)

      setEvaluationResult(result)

      setFeedbackDecisionId(decisionId)
      // Let the user explicitly choose what they actually selected.
      setFeedbackOptionId('')
      setFeedbackRating(5)
      setFeedbackNotes('')
      setCriterionRatings({})
      setFeedbackError('')
      setFeedbackMessage('')

      const updatedDecisions =
        await getUserDecisions(userId)

      setDecisions(updatedDecisions)
    } catch (error) {
      console.error(
        'Failed to evaluate decision:',
        error,
      )

      setEvaluationError(
        error.response?.data?.detail ||
        'Unable to evaluate this decision. Please try again.',
      )
    } finally {
      setEvaluatingDecisionId(null)
    }
  }


  const handleSubmitFeedback = async (event) => {
    event.preventDefault()

    // Prevent rapid duplicate submissions for the same decision before
    // React has time to re-render.
    const decisionLockKey = feedbackDecisionId
      ? String(feedbackDecisionId)
      : ''

    if (decisionLockKey && feedbackSubmitLock.current.has(decisionLockKey)) {
      return
    }

    const hasAlreadySubmittedFeedback =
      Boolean(feedbackDecisionId) &&
      (feedbackSubmittedDecisionIds.has(String(feedbackDecisionId)) ||
        feedbackRecords.some(
          (record) =>
            String(record.decision_id) === String(feedbackDecisionId),
        ))

    if (hasAlreadySubmittedFeedback) {
      setFeedbackError('')
      setFeedbackMessage(
        'Feedback has already been submitted for this decision. Your preference profile will not be updated again.',
      )
      return
    }

    setFeedbackError('')
    setFeedbackMessage('')

    if (!userId || !feedbackDecisionId || !feedbackOptionId) {
      setFeedbackError(
        'Please select the option you actually chose before submitting feedback.',
      )
      return
    }

    const payload = {
      user_id: userId,
      decision_id: feedbackDecisionId,
      chosen_option_id: feedbackOptionId,
      rating: Number(feedbackRating),
      notes: feedbackNotes.trim() || null,
      criterion_ratings: criterionRatings,
    }

    let feedbackSaved = false

    try {
      feedbackSubmitLock.current.add(decisionLockKey)
      setSubmittingFeedback(true)
      const savedFeedback = await submitFeedback(payload)
      feedbackSaved = true
      setFeedbackSubmittedDecisionIds((current) => {
        const next = new Set(current)
        next.add(String(feedbackDecisionId))
        return next
      })
      setFeedbackMessage('Feedback saved. Updating your preference profile...')

      try {
        const learningResult = await learnFromFeedback(savedFeedback.id)
        const updatedPreferences = learningResult.updated_preferences || []

        try {
          const refreshedPreferences = await getUserPreferences(userId)
          setPreferences(refreshedPreferences)
        } catch (refreshError) {
          console.warn(
            'Feedback was processed, but preferences could not be refreshed:',
            refreshError,
          )
        }

        await refreshLearningHistory()
        await refreshFeedbackRecords()

        setFeedbackMessage(
          updatedPreferences.length > 0
            ? `Feedback saved — ${updatedPreferences.length} preference(s) updated.`
            : learningResult.message ||
            'Feedback saved. No preference weights changed for these ratings.',
        )
      } catch (learningError) {
        console.error('Feedback saved, but preference learning failed:', learningError)
        setFeedbackMessage(
          'Feedback was saved, but preference learning could not be completed. Check the backend and try again.',
        )
      }
    } catch (error) {
      console.error('Failed to submit feedback:', error)
      setFeedbackError(
        error.response?.data?.detail ||
        'Unable to save feedback. Please try again.',
      )
    } finally {
      // Keep the lock when feedback was persisted; unlock only if saving failed.
      if (!feedbackSaved && decisionLockKey) {
        feedbackSubmitLock.current.delete(decisionLockKey)
      }
      setSubmittingFeedback(false)
    }
  }

  const feedbackAlreadySubmitted =
    Boolean(feedbackDecisionId) &&
    (feedbackSubmittedDecisionIds.has(String(feedbackDecisionId)) ||
      feedbackRecords.some(
        (record) =>
          String(record.decision_id) === String(feedbackDecisionId),
      ))

  const completedDecisions = decisions.filter(
    (decision) => decision.status === 'completed',
  )

  const validFeedbackRecords = feedbackRecords
    .map((record) => ({
      ...record,
      normalizedRating: Number(record.rating ?? record.overall_rating),
      normalizedDate: record.created_at ? new Date(record.created_at) : null,
    }))
    .filter(
      (record) =>
        Number.isFinite(record.normalizedRating) &&
        record.normalizedRating >= 1 &&
        record.normalizedRating <= 5,
    )

  const averageFeedbackRating = validFeedbackRecords.length
    ? validFeedbackRecords.reduce(
      (total, record) => total + record.normalizedRating,
      0,
    ) / validFeedbackRecords.length
    : null

  const satisfiedFeedbackCount = validFeedbackRecords.filter(
    (record) => record.normalizedRating >= 4,
  ).length

  const satisfactionRate = validFeedbackRecords.length
    ? Math.round((satisfiedFeedbackCount / validFeedbackRecords.length) * 100)
    : null

  const decisionCompletionRate = decisions.length
    ? Math.round((completedDecisions.length / decisions.length) * 100)
    : 0

  const preferenceIncreases = learningHistory.filter(
    (entry) => Number(entry.new_weight) > Number(entry.old_weight),
  ).length

  const preferenceDecreases = learningHistory.filter(
    (entry) => Number(entry.new_weight) < Number(entry.old_weight),
  ).length

  const analyticsPreferenceData = [...preferences].sort(
    (a, b) => Number(b.weight) - Number(a.weight),
  )

  const currentMonth = new Date()
  currentMonth.setDate(1)
  currentMonth.setHours(0, 0, 0, 0)

  const monthlyActivity = Array.from({ length: 6 }, (_, index) => {
    const month = new Date(
      currentMonth.getFullYear(),
      currentMonth.getMonth() - (5 - index),
      1,
    )
    const nextMonth = new Date(month.getFullYear(), month.getMonth() + 1, 1)
    const monthDecisions = decisions.filter((decision) => {
      if (!decision.created_at) return false
      const timestamp = new Date(decision.created_at).getTime()
      return Number.isFinite(timestamp) && timestamp >= month.getTime() && timestamp < nextMonth.getTime()
    }).length
    const monthFeedback = validFeedbackRecords.filter((record) => {
      if (!record.normalizedDate) return false
      const timestamp = record.normalizedDate.getTime()
      return Number.isFinite(timestamp) && timestamp >= month.getTime() && timestamp < nextMonth.getTime()
    }).length

    return {
      key: `${month.getFullYear()}-${month.getMonth()}`,
      label: month.toLocaleDateString(undefined, { month: 'short' }),
      decisions: monthDecisions,
      feedback: monthFeedback,
    }
  })

  const maxMonthlyActivity = Math.max(
    1,
    ...monthlyActivity.flatMap((month) => [month.decisions, month.feedback]),
  )

  const feedbackRatingDistribution = [1, 2, 3, 4, 5].map((rating) => ({
    rating,
    count: validFeedbackRecords.filter(
      (record) => record.normalizedRating === rating,
    ).length,
  }))
  const maxRatingCount = Math.max(
    1,
    ...feedbackRatingDistribution.map((item) => item.count),
  )

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">D</div>

          <div>
            <h1>DecisionOS</h1>
            <span>Personal Decision Engine</span>
          </div>
        </div>

        <nav className="navigation">
          <p className="nav-label">MAIN</p>

          <button
            className={activeNavItem === 'dashboard' ? 'nav-item active' : 'nav-item'}
            onClick={() => navigateToSection('dashboard', 'dashboard-top')}
          >
            <span className="nav-icon">⌂</span>
            Dashboard
          </button>

          <button
            className={activeNavItem === 'preferences' ? 'nav-item active' : 'nav-item'}
            onClick={() => navigateToSection('preferences', 'preference-profile')}
          >
            <span className="nav-icon">◈</span>
            Preferences
          </button>

          <button
            className={activeNavItem === 'decisions' ? 'nav-item active' : 'nav-item'}
            onClick={() => navigateToSection('decisions', 'decision-history')}
          >
            <span className="nav-icon">◇</span>
            Decisions
          </button>

          <button
            className={activeNavItem === 'analytics' ? 'nav-item active' : 'nav-item'}
            onClick={() => navigateToSection('analytics', 'analytics-dashboard')}
          >
            <span className="nav-icon">▥</span>
            Analytics
          </button>

          <button
            className={activeNavItem === 'history' ? 'nav-item active' : 'nav-item'}
            onClick={() => navigateToSection('history', 'learning-history')}
          >
            <span className="nav-icon">↺</span>
            History
          </button>
        </nav>

        <div className="sidebar-bottom">
          <div className="ai-status">
            <div className="status-dot"></div>

            <div>
              <strong>AI Engine</strong>
              <span>Ready</span>
            </div>
          </div>

          <div className="user-card">
            <div className="avatar">U</div>

            <div>
              <strong>Decision User</strong>
              <span>Personal Profile</span>
            </div>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header id="dashboard-top" className="topbar">
          <div>
            <p className="eyebrow">
              PERSONAL DECISION INTELLIGENCE
            </p>

            <h2>Good morning 👋</h2>

            <p className="topbar-description">
              Make better decisions based on what matters
              to you.
            </p>
          </div>

          <button
            className="primary-button"
            onClick={openCreateDecisionModal}
          >
            + New Decision
          </button>
        </header>

        <section className="hero-card">
          <div className="hero-content">
            <span className="hero-badge">
              AI-POWERED DECISION ENGINE
            </span>

            <h3>
              Your preferences.
              <br />
              Your decisions.
              <br />
              <span>Better outcomes.</span>
            </h3>

            <p>
              DecisionOS learns what matters to you,
              compares your options, explains the
              trade-offs, and improves from your feedback.
            </p>

            <button
              className="hero-button"
              onClick={openCreateDecisionModal}
            >
              Create a decision
              <span>→</span>
            </button>
          </div>

          <div className="hero-visual">
            <div className="decision-orbit orbit-one"></div>
            <div className="decision-orbit orbit-two"></div>

            <div className="decision-core">
              <span>AI</span>
            </div>

            <div className="orbit-card card-one">
              <span>Preference</span>

              <strong>
                {preferences.length > 0
                  ? preferences[0].criterion
                  : 'Loading'}
              </strong>

              <small>
                {preferences.length > 0
                  ? `${Math.round(
                    preferences[0].weight * 100,
                  )}% priority`
                  : 'Loading preference'}
              </small>
            </div>

            <div className="orbit-card card-two">
              <span>Recommendation</span>

              <strong>
                {completedDecisions.length > 0
                  ? 'Available'
                  : 'Waiting'}
              </strong>

              <small>
                {completedDecisions.length} completed
              </small>
            </div>
          </div>
        </section>

        <section className="stats-grid">
          <div className="stat-card">
            <div className="stat-header">
              <span>Preferences</span>

              <div className="stat-icon purple">
                ◈
              </div>
            </div>

            <strong>
              {loadingPreferences
                ? '...'
                : preferences.length}
            </strong>

            <p>Active preferences</p>
          </div>

          <div className="stat-card">
            <div className="stat-header">
              <span>Decisions</span>

              <div className="stat-icon blue">
                ◇
              </div>
            </div>

            <strong>
              {loadingDecisions
                ? '...'
                : decisions.length}
            </strong>

            <p>Total decisions</p>
          </div>

          <div className="stat-card">
            <div className="stat-header">
              <span>Completed</span>

              <div className="stat-icon green">
                ✓
              </div>
            </div>

            <strong>
              {loadingDecisions
                ? '...'
                : completedDecisions.length}
            </strong>

            <p>Evaluated decisions</p>
          </div>

          <div className="stat-card">
            <div className="stat-header">
              <span>Learning</span>

              <div className="stat-icon orange">
                ↗
              </div>
            </div>

            <strong>Active</strong>

            <p>Preference learning enabled</p>
          </div>
        </section>

        <section className="content-grid">
          <div id="preference-profile" className="panel">
            <div className="panel-header">
              <div>
                <span className="section-label">
                  YOUR PROFILE
                </span>

                <h3>Preference Profile</h3>
              </div>

              <button className="text-button">
                View all →
              </button>
            </div>

            {preferenceError && (
              <div className="api-error">
                <strong>
                  Preference loading error
                </strong>

                <span>{preferenceError}</span>
              </div>
            )}

            {loadingPreferences ? (
              <div className="empty-state">
                <strong>
                  Loading preferences...
                </strong>

                <span>
                  Fetching your profile from DecisionOS.
                </span>
              </div>
            ) : preferences.length === 0 ? (
              <div className="empty-state">
                <strong>
                  No preferences configured
                </strong>

                <span>
                  Add preferences to personalize
                  decisions.
                </span>
              </div>
            ) : (
              <div className="preference-list">
                {preferences.map((preference) => {
                  const value = Math.round(
                    preference.weight * 100,
                  )

                  const displayName =
                    preference.criterion
                      .charAt(0)
                      .toUpperCase() +
                    preference.criterion.slice(1)

                  const direction =
                    preference.direction ===
                      'minimize'
                      ? 'Minimize'
                      : 'Maximize'

                  return (
                    <div
                      className="preference-row"
                      key={preference.id}
                    >
                      <div className="preference-info">
                        <div className="preference-name">
                          <strong>
                            {displayName}
                          </strong>

                          <span
                            className={
                              preference.direction ===
                                'minimize'
                                ? 'direction minimize'
                                : 'direction maximize'
                            }
                          >
                            {direction}
                          </span>
                        </div>

                        <div className="progress-track">
                          <div
                            className="progress-fill"
                            style={{
                              width: `${value}%`,
                            }}
                          ></div>
                        </div>
                      </div>

                      <strong className="preference-value">
                        {value}%
                      </strong>
                    </div>
                  )
                })}
              </div>
            )}
          </div>

          <div className="panel">
            <div className="panel-header">
              <div>
                <span className="section-label">
                  QUICK ACTIONS
                </span>

                <h3>
                  What do you want to decide?
                </h3>
              </div>
            </div>

            <div className="quick-actions">
              <button
                className="quick-action"
                onClick={openCreateDecisionModal}
              >
                <span className="quick-icon">
                  ◉
                </span>

                <span>
                  <strong>
                    Compare Products
                  </strong>

                  <small>
                    Laptops, phones, gadgets
                  </small>
                </span>

                <span className="arrow">→</span>
              </button>

              <button
                className="quick-action"
                onClick={openCreateDecisionModal}
              >
                <span className="quick-icon">
                  ◆
                </span>

                <span>
                  <strong>
                    Compare Courses
                  </strong>

                  <small>
                    Choose your next course
                  </small>
                </span>

                <span className="arrow">→</span>
              </button>

              <button
                className="quick-action"
                onClick={openCreateDecisionModal}
              >
                <span className="quick-icon">
                  ✦
                </span>

                <span>
                  <strong>
                    Compare Jobs
                  </strong>

                  <small>
                    Find the right opportunity
                  </small>
                </span>

                <span className="arrow">→</span>
              </button>
            </div>
          </div>
        </section>

        <section id="decision-history" className="panel decisions-panel">
          <div className="panel-header">
            <div>
              <span className="section-label">
                DECISION HISTORY
              </span>

              <h3>Recent Decisions</h3>
            </div>

            <button className="text-button">
              View history →
            </button>
          </div>

          {decisionError && (
            <div className="api-error">
              <strong>
                Backend connection error
              </strong>

              <span>{decisionError}</span>
            </div>
          )}

          {evaluationError && (
            <div className="api-error">
              <strong>
                Decision evaluation failed
              </strong>

              <span>{evaluationError}</span>
            </div>
          )}

          {loadingDecisions ? (
            <div className="empty-state">
              <strong>
                Loading decisions...
              </strong>

              <span>
                Fetching your decisions from
                DecisionOS.
              </span>
            </div>
          ) : decisions.length === 0 ? (
            <div className="empty-state">
              <strong>No decisions yet</strong>

              <span>
                Create your first decision to get
                started.
              </span>
            </div>
          ) : (
            <div className="decision-table">
              <div className="table-header">
                <span>Decision</span>
                <span>Category</span>
                <span>Recommendation</span>
                <span>Status</span>
                <span>Created</span>
                <span>Action</span>
              </div>

              {decisions.map((decision) => {
                const recommendedOption =
                  decision.options?.find(
                    (option) =>
                      option.id ===
                      decision.chosen_option_id,
                  )

                const isEvaluating =
                  evaluatingDecisionId ===
                  decision.id

                return (
                  <div
                    className="table-row"
                    key={decision.id}
                  >
                    <strong>
                      {decision.title}
                    </strong>

                    <span>
                      {decision.category ||
                        'General'}
                    </span>

                    <span className="recommendation">
                      {recommendedOption
                        ? recommendedOption.name
                        : decision.status ===
                          'completed'
                          ? 'Completed'
                          : 'Pending'}
                    </span>

                    <span>
                      <span
                        className={
                          decision.status ===
                            'completed'
                            ? 'status completed'
                            : 'status draft'
                        }
                      >
                        {decision.status}
                      </span>
                    </span>

                    <span>
                      {new Date(
                        decision.created_at,
                      ).toLocaleDateString()}
                    </span>

                    <span>
                      {decision.status ===
                        'draft' ? (
                        <button
                          type="button"
                          className="evaluate-button"
                          onClick={() =>
                            handleEvaluateDecision(
                              decision.id,
                            )
                          }
                          disabled={isEvaluating}
                        >
                          {isEvaluating
                            ? 'Evaluating...'
                            : 'Evaluate'}
                        </button>
                      ) : (
                        <span className="evaluated-label">
                          Evaluated
                        </span>
                      )}
                    </span>
                  </div>
                )
              })}
            </div>
          )}
        </section>

        {evaluationResult && (
          <section className="panel decision-result-panel">
            <div className="panel-header">
              <div>
                <span className="section-label">
                  AI DECISION RESULT
                </span>

                <h3>
                  Your Personalized
                  Recommendation
                </h3>
              </div>

              <span className="status completed">
                Completed
              </span>
            </div>

            <div className="result-top-grid">
              <div className="recommendation-card">
                <span className="section-label">
                  TOP RECOMMENDATION
                </span>

                <h3>
                  {evaluationResult
                    .recommendation?.name}
                </h3>

                <p>
                  {evaluationResult
                    .recommendation?.description}
                </p>

                <strong className="result-score">
                  {(
                    (evaluationResult
                      .recommendation
                      ?.score ?? 0) * 100
                  ).toFixed(1)}
                  %
                </strong>

                <span className="score-label">
                  Overall decision score
                </span>
              </div>

              <div className="explanation-card">
                <span className="section-label">
                  AI EXPLANATION
                </span>

                <p>
                  {evaluationResult.explanation}
                </p>
              </div>
            </div>

            <div className="ranked-options-section">
              <span className="section-label">
                RANKED OPTIONS
              </span>

              <div className="ranked-options-list">
                {evaluationResult.ranked_options?.map(
                  (item) => (
                    <div
                      className={
                        item.rank === 1
                          ? 'ranked-option recommended'
                          : 'ranked-option'
                      }
                      key={item.option.id}
                    >
                      <div className="rank-number">
                        #{item.rank}
                      </div>

                      <div className="rank-option-info">
                        <strong>
                          {item.option.name}
                        </strong>

                        <span>
                          {item.option.description}
                        </span>

                        <div className="tradeoff-lines">
                          <span>
                            <strong>
                              Strengths:
                            </strong>{' '}
                            {item.tradeoffs
                              ?.strengths
                              ?.length
                              ? item.tradeoffs.strengths.join(
                                ', ',
                              )
                              : 'None'}
                          </span>

                          <span>
                            <strong>
                              Weaknesses:
                            </strong>{' '}
                            {item.tradeoffs
                              ?.weaknesses
                              ?.length
                              ? item.tradeoffs.weaknesses.join(
                                ', ',
                              )
                              : 'None'}
                          </span>
                        </div>
                      </div>

                      <div className="rank-score">
                        {(
                          item.score * 100
                        ).toFixed(1)}
                        %
                      </div>
                    </div>
                  ),
                )}
              </div>
            </div>

            <div className="feedback-section">
              <div className="feedback-heading">
                <span className="section-label">HELP DECISIONOS LEARN</span>
                <h3>How did this decision turn out?</h3>
                <p>
                  Tell DecisionOS what you chose, how satisfied you are, and
                  which priorities matter most for future decisions.
                </p>
              </div>

              <form className="feedback-form" onSubmit={handleSubmitFeedback}>
                <label>
                  <span>Which option did you actually choose?</span>
                  <select
                    value={feedbackOptionId}
                    onChange={(event) => setFeedbackOptionId(event.target.value)}
                    disabled={submittingFeedback || feedbackAlreadySubmitted}
                    required
                  >
                    <option value="">Select your chosen option</option>
                    {(evaluationResult.ranked_options || [])
                      .map((item) => item.option)
                      .filter(Boolean)
                      .map((option) => (
                        <option key={option.id} value={option.id}>
                          {option.name}
                        </option>
                      ))}
                  </select>
                </label>

                <label>
                  <span>Overall satisfaction</span>
                  <select
                    value={feedbackRating}
                    onChange={(event) =>
                      setFeedbackRating(Number(event.target.value))
                    }
                    disabled={submittingFeedback || feedbackAlreadySubmitted}
                    required
                  >
                    <option value={1}>1 — Very dissatisfied</option>
                    <option value={2}>2 — Dissatisfied</option>
                    <option value={3}>3 — Neutral</option>
                    <option value={4}>4 — Satisfied</option>
                    <option value={5}>5 — Very satisfied</option>
                  </select>
                </label>

                {preferences.length > 0 && (
                  <div className="criterion-feedback">
                    <div className="criterion-feedback-intro">
                      <strong>How important is each priority? (optional)</strong>
                      <p>
                        Rate how important each criterion should be in future
                        decisions. Ratings 1–2 decrease its weight, 3 keeps it
                        unchanged, and ratings 4–5 increase its weight.
                      </p>
                    </div>

                    {preferences.map((preference) => (
                      <label key={preference.id}>
                        <span>
                          {preference.criterion.charAt(0).toUpperCase() +
                            preference.criterion.slice(1)}
                        </span>
                        <select
                          value={criterionRatings[preference.criterion] ?? ''}
                          disabled={submittingFeedback || feedbackAlreadySubmitted}
                          onChange={(event) => {
                            const value = event.target.value
                            setCriterionRatings((current) => {
                              const next = { ...current }
                              if (value) {
                                next[preference.criterion] = Number(value)
                              } else {
                                delete next[preference.criterion]
                              }
                              return next
                            })
                          }}
                        >
                          <option value="">Not rated</option>
                          <option value={1}>1 — Not important</option>
                          <option value={2}>2 — Slightly important</option>
                          <option value={3}>3 — Moderately important (no change)</option>
                          <option value={4}>4 — Very important</option>
                          <option value={5}>5 — Extremely important</option>
                        </select>
                      </label>
                    ))}
                  </div>
                )}

                <label className="feedback-notes">
                  <span>Notes (optional)</span>
                  <textarea
                    value={feedbackNotes}
                    onChange={(event) => setFeedbackNotes(event.target.value)}
                    disabled={submittingFeedback || feedbackAlreadySubmitted}
                    placeholder="What worked well? What would you change next time?"
                    rows={3}
                    maxLength={5000}
                  />
                </label>

                {feedbackError && (
                  <div className="api-error">
                    <strong>Could not save feedback</strong>
                    <span>{feedbackError}</span>
                  </div>
                )}

                {feedbackMessage && (
                  <div className="feedback-message" role="status">
                    {feedbackMessage}
                  </div>
                )}

                <button
                  type="submit"
                  className="primary-button"
                  disabled={submittingFeedback || feedbackAlreadySubmitted}
                >
                  {submittingFeedback
                    ? 'Saving feedback...'
                    : feedbackAlreadySubmitted
                      ? 'Feedback already submitted'
                      : 'Submit feedback & learn'}
                </button>
              </form>
            </div>
          </section>
        )}

        <section id="analytics-dashboard" className="panel analytics-panel">
          <div className="panel-header analytics-panel-header">
            <div>
              <span className="section-label">YOUR DATA, MADE CLEAR</span>
              <h3>Decision Analytics</h3>
              <p className="analytics-description">
                Real patterns calculated from your decisions, submitted feedback,
                current preferences, and recorded learning events.
              </p>
            </div>
            <button
              type="button"
              className="text-button"
              onClick={() => {
                refreshFeedbackRecords()
                refreshLearningHistory()
              }}
              disabled={loadingFeedbackRecords || loadingLearningHistory}
            >
              {loadingFeedbackRecords || loadingLearningHistory
                ? 'Refreshing...'
                : 'Refresh analytics →'}
            </button>
          </div>

          {(feedbackRecordsError || learningHistoryError) && (
            <div className="api-error analytics-error">
              <strong>Some analytics data could not be loaded</strong>
              <span>
                {[feedbackRecordsError, learningHistoryError].filter(Boolean).join(' ')}
              </span>
            </div>
          )}

          <div className="analytics-metrics-grid">
            <article className="analytics-metric-card">
              <span>Decisions created</span>
              <strong>{loadingDecisions ? '…' : decisions.length}</strong>
              <small>All recorded decisions</small>
            </article>
            <article className="analytics-metric-card">
              <span>Completion rate</span>
              <strong>{loadingDecisions ? '…' : `${decisionCompletionRate}%`}</strong>
              <small>{completedDecisions.length} evaluated of {decisions.length}</small>
            </article>
            <article className="analytics-metric-card">
              <span>Average satisfaction</span>
              <strong>
                {loadingFeedbackRecords
                  ? '…'
                  : averageFeedbackRating === null
                    ? '—'
                    : `${averageFeedbackRating.toFixed(1)}/5`}
              </strong>
              <small>
                {validFeedbackRecords.length
                  ? `${validFeedbackRecords.length} feedback response${validFeedbackRecords.length === 1 ? '' : 's'}`
                  : 'No feedback ratings yet'}
              </small>
            </article>
            <article className="analytics-metric-card">
              <span>Preference updates</span>
              <strong>{loadingLearningHistory ? '…' : learningHistory.length}</strong>
              <small>Recorded weight changes</small>
            </article>
          </div>

          <div className="analytics-content-grid">
            <article className="analytics-chart-card analytics-chart-wide">
              <div className="analytics-chart-heading">
                <div>
                  <h4>Activity over time</h4>
                  <p>Decisions created and feedback submitted, by month</p>
                </div>
                <span className="analytics-chart-period">Last 6 months</span>
              </div>

              {loadingDecisions || loadingFeedbackRecords ? (
                <div className="empty-state analytics-empty-state">
                  <strong>Loading activity…</strong>
                  <span>Preparing your monthly timeline.</span>
                </div>
              ) : (
                <>
                  <div className="analytics-activity-chart" role="img" aria-label="Monthly counts of decisions created and feedback submitted">
                    {monthlyActivity.map((month) => (
                      <div className="analytics-month-column" key={month.key}>
                        <div className="analytics-bars-area">
                          <div className="analytics-bar-pair">
                            <div
                              className="analytics-bar analytics-bar-decisions"
                              style={{ height: `${Math.max((month.decisions / maxMonthlyActivity) * 100, month.decisions ? 4 : 0)}%` }}
                              title={`${month.decisions} decisions`}
                            />
                            <div
                              className="analytics-bar analytics-bar-feedback"
                              style={{ height: `${Math.max((month.feedback / maxMonthlyActivity) * 100, month.feedback ? 4 : 0)}%` }}
                              title={`${month.feedback} feedback responses`}
                            />
                          </div>
                          <span className="analytics-month-total">{month.decisions + month.feedback || ''}</span>
                        </div>
                        <span className="analytics-month-label">{month.label}</span>
                      </div>
                    ))}
                  </div>
                  <div className="analytics-legend">
                    <span><i className="analytics-legend-dot decisions-dot" /> Decisions</span>
                    <span><i className="analytics-legend-dot feedback-dot" /> Feedback</span>
                  </div>
                </>
              )}
            </article>

            <article className="analytics-chart-card">
              <div className="analytics-chart-heading">
                <div>
                  <h4>Feedback ratings</h4>
                  <p>Distribution of submitted satisfaction scores</p>
                </div>
              </div>

              {loadingFeedbackRecords ? (
                <div className="empty-state analytics-empty-state">
                  <strong>Loading ratings…</strong>
                </div>
              ) : validFeedbackRecords.length === 0 ? (
                <div className="empty-state analytics-empty-state">
                  <strong>No ratings to chart yet</strong>
                  <span>Submit feedback after a decision to build this view.</span>
                </div>
              ) : (
                <div className="analytics-rating-list">
                  {feedbackRatingDistribution.map((item) => (
                    <div className="analytics-rating-row" key={item.rating}>
                      <span className="analytics-rating-label">{item.rating} <span aria-hidden="true">★</span></span>
                      <div className="analytics-inline-bar-track">
                        <div
                          className="analytics-inline-bar-fill rating-bar-fill"
                          style={{ width: `${(item.count / maxRatingCount) * 100}%` }}
                        />
                      </div>
                      <strong>{item.count}</strong>
                    </div>
                  ))}
                  <div className="analytics-insight-line">
                    {satisfactionRate}% of ratings are positive (4 or 5)
                  </div>
                </div>
              )}
            </article>

            <article className="analytics-chart-card">
              <div className="analytics-chart-heading">
                <div>
                  <h4>Current preference weights</h4>
                  <p>Relative importance in your profile</p>
                </div>
              </div>

              {loadingPreferences ? (
                <div className="empty-state analytics-empty-state">
                  <strong>Loading preferences…</strong>
                </div>
              ) : analyticsPreferenceData.length === 0 ? (
                <div className="empty-state analytics-empty-state">
                  <strong>No preferences configured</strong>
                  <span>Add preferences before comparing options.</span>
                </div>
              ) : (
                <div className="analytics-preference-list">
                  {analyticsPreferenceData.map((preference) => {
                    const weight = Math.max(0, Math.min(1, Number(preference.weight) || 0))
                    const label = preference.criterion
                      ? preference.criterion.charAt(0).toUpperCase() + preference.criterion.slice(1)
                      : 'Preference'
                    return (
                      <div className="analytics-preference-row" key={preference.id}>
                        <div className="analytics-preference-row-top">
                          <span>{label}</span>
                          <strong>{Math.round(weight * 100)}%</strong>
                        </div>
                        <div className="analytics-inline-bar-track">
                          <div
                            className="analytics-inline-bar-fill preference-bar-fill"
                            style={{ width: `${weight * 100}%` }}
                          />
                        </div>
                        <small>{preference.direction === 'minimize' ? 'Lower is better' : 'Higher is better'}</small>
                      </div>
                    )
                  })}
                </div>
              )}
            </article>

            <article className="analytics-chart-card">
              <div className="analytics-chart-heading">
                <div>
                  <h4>Learning activity</h4>
                  <p>How recorded preference weights have moved</p>
                </div>
              </div>

              {loadingLearningHistory ? (
                <div className="empty-state analytics-empty-state">
                  <strong>Loading learning events…</strong>
                </div>
              ) : learningHistory.length === 0 ? (
                <div className="empty-state analytics-empty-state">
                  <strong>No learning events yet</strong>
                  <span>Criterion feedback creates the first entries.</span>
                </div>
              ) : (
                <div className="analytics-learning-summary">
                  <div className="analytics-change-stat increase-stat">
                    <span className="analytics-change-icon">↑</span>
                    <div><strong>{preferenceIncreases}</strong><span>Increased</span></div>
                  </div>
                  <div className="analytics-change-stat decrease-stat">
                    <span className="analytics-change-icon">↓</span>
                    <div><strong>{preferenceDecreases}</strong><span>Decreased</span></div>
                  </div>
                  <div className="analytics-learning-footnote">
                    {preferenceIncreases + preferenceDecreases} non-neutral changes recorded across {new Set(learningHistory.map((entry) => entry.criterion)).size} criteria.
                  </div>
                </div>
              )}
            </article>
          </div>
        </section>

        <section id="learning-history" className="panel learning-history-panel">
          <div className="panel-header learning-history-header">
            <div>
              <span className="section-label">PERSONALIZATION AUDIT</span>
              <h3>Learning History</h3>
              <p className="learning-history-description">
                See how your feedback changes your preference weights over time.
              </p>
            </div>
            <button
              type="button"
              className="text-button"
              onClick={refreshLearningHistory}
              disabled={loadingLearningHistory}
            >
              {loadingLearningHistory ? 'Refreshing...' : 'Refresh history →'}
            </button>
          </div>

          {learningHistoryError && (
            <div className="api-error">
              <strong>Learning history unavailable</strong>
              <span>{learningHistoryError}</span>
            </div>
          )}

          {loadingLearningHistory ? (
            <div className="empty-state">
              <strong>Loading learning history...</strong>
              <span>Fetching your preference changes from DecisionOS.</span>
            </div>
          ) : learningHistory.length === 0 ? (
            <div className="empty-state">
              <strong>No learning events yet</strong>
              <span>
                Evaluate a decision and submit criterion ratings to see how
                your preference profile changes here.
              </span>
            </div>
          ) : (
            <div className="learning-history-list">
              {[...learningHistory]
                .sort(
                  (a, b) => new Date(b.created_at) - new Date(a.created_at),
                )
                .map((entry) => {
                  const oldWeight = Number(entry.old_weight ?? 0)
                  const newWeight = Number(entry.new_weight ?? 0)
                  const delta = newWeight - oldWeight
                  const deltaPoints = Math.abs(delta * 100).toFixed(1)
                  const criterionName = entry.criterion
                    ? entry.criterion.charAt(0).toUpperCase() + entry.criterion.slice(1)
                    : 'Preference'
                  const sourceLabel = entry.source?.startsWith('feedback:')
                    ? 'Feedback update'
                    : entry.source || 'Preference update'

                  return (
                    <article className="learning-history-entry" key={entry.id}>
                      <div className="learning-history-entry-top">
                        <div>
                          <h4>{criterionName}</h4>
                          <span className="learning-history-source">{sourceLabel}</span>
                        </div>
                        <time dateTime={entry.created_at}>
                          {entry.created_at
                            ? new Date(entry.created_at).toLocaleString()
                            : 'Date unavailable'}
                        </time>
                      </div>

                      <div className="history-weight-comparison">
                        <div className="history-weight-cell">
                          <span>Previous weight</span>
                          <strong>{(oldWeight * 100).toFixed(0)}%</strong>
                        </div>
                        <span className="history-weight-arrow" aria-hidden="true">→</span>
                        <div className="history-weight-cell current">
                          <span>New weight</span>
                          <strong>{(newWeight * 100).toFixed(0)}%</strong>
                        </div>
                        <span
                          className={`history-weight-delta ${delta > 0 ? 'increased' : delta < 0 ? 'decreased' : 'unchanged'}`}
                        >
                          {delta > 0
                            ? `↑ Increased by ${deltaPoints} points`
                            : delta < 0
                              ? `↓ Decreased by ${deltaPoints} points`
                              : 'No change'}
                        </span>
                      </div>

                      <p className="learning-history-reason">
                        <strong>Why:</strong> {entry.reason || 'No explanation was recorded.'}
                      </p>
                    </article>
                  )
                })}
            </div>
          )}
        </section>

        <footer className="footer">
          <span>DecisionOS</span>

          <span>
            Personal AI Decision Engine
          </span>
        </footer>
      </main>

      {isCreateModalOpen && (
        <div
          className="modal-backdrop"
          onMouseDown={(event) => {
            if (
              event.target ===
              event.currentTarget
            ) {
              closeCreateDecisionModal()
            }
          }}
        >
          <div
            className="create-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="create-decision-title"
          >
            <div className="modal-header">
              <div>
                <span className="section-label">
                  NEW DECISION
                </span>

                <h3 id="create-decision-title">
                  Create a decision
                </h3>

                <p>
                  Add the choices you want
                  DecisionOS to compare against
                  your preference profile.
                </p>
              </div>

              <button
                type="button"
                className="modal-close"
                onClick={closeCreateDecisionModal}
                disabled={creatingDecision}
                aria-label="Close"
              >
                ×
              </button>
            </div>

            <form
              className="create-decision-form"
              onSubmit={handleCreateDecision}
            >
              <div className="form-section">
                <label>
                  <span>Decision title</span>

                  <input
                    type="text"
                    value={newDecision.title}
                    onChange={(event) =>
                      handleDecisionFieldChange(
                        'title',
                        event.target.value,
                      )
                    }
                    placeholder="e.g. Choose my next laptop"
                    maxLength={200}
                    autoFocus
                  />
                </label>

                <label>
                  <span>Description</span>

                  <textarea
                    value={
                      newDecision.description
                    }
                    onChange={(event) =>
                      handleDecisionFieldChange(
                        'description',
                        event.target.value,
                      )
                    }
                    placeholder="What are you trying to decide?"
                    rows={3}
                  />
                </label>
              </div>

              <div className="form-section">
                <div className="options-heading">
                  <div>
                    <span className="section-label">
                      CANDIDATE OPTIONS
                    </span>

                    <h4>
                      What are you comparing?
                    </h4>
                  </div>

                  <button
                    type="button"
                    className="add-option-button"
                    onClick={addOption}
                    disabled={creatingDecision}
                  >
                    + Add Option
                  </button>
                </div>

                <div className="create-options-list">
                  {newDecision.options.map(
                    (
                      option,
                      optionIndex,
                    ) => (
                      <div
                        className="create-option-card"
                        key={`option-${optionIndex}`}
                      >
                        <div className="create-option-header">
                          <strong>
                            Option{' '}
                            {optionIndex + 1}
                          </strong>

                          {newDecision
                            .options.length >
                            2 && (
                              <button
                                type="button"
                                className="remove-option-button"
                                onClick={() =>
                                  removeOption(
                                    optionIndex,
                                  )
                                }
                                disabled={
                                  creatingDecision
                                }
                              >
                                Remove
                              </button>
                            )}
                        </div>

                        <div className="form-grid">
                          <label>
                            <span>Name</span>

                            <input
                              type="text"
                              value={
                                option.name
                              }
                              onChange={(
                                event,
                              ) =>
                                handleOptionFieldChange(
                                  optionIndex,
                                  'name',
                                  event
                                    .target
                                    .value,
                                )
                              }
                              placeholder={`Option ${optionIndex + 1
                                }`}
                              maxLength={200}
                            />
                          </label>

                          <label>
                            <span>
                              Description
                            </span>

                            <input
                              type="text"
                              value={
                                option.description
                              }
                              onChange={(
                                event,
                              ) =>
                                handleOptionFieldChange(
                                  optionIndex,
                                  'description',
                                  event
                                    .target
                                    .value,
                                )
                              }
                              placeholder="Optional description"
                            />
                          </label>
                        </div>

                        {preferences.length >
                          0 && (
                            <div className="attribute-grid">
                              {preferences.map(
                                (
                                  preference,
                                ) => {
                                  const displayName =
                                    preference.criterion
                                      .charAt(
                                        0,
                                      )
                                      .toUpperCase() +
                                    preference.criterion.slice(
                                      1,
                                    )

                                  return (
                                    <label
                                      key={`${optionIndex}-${preference.id}`}
                                    >
                                      <span>
                                        {
                                          displayName
                                        }
                                      </span>

                                      <input
                                        type="number"
                                        step="any"
                                        value={
                                          option
                                            .attributes[
                                          preference
                                            .criterion
                                          ] ??
                                          ''
                                        }
                                        onChange={(
                                          event,
                                        ) =>
                                          handleOptionAttributeChange(
                                            optionIndex,
                                            preference.criterion,
                                            event
                                              .target
                                              .value,
                                          )
                                        }
                                        placeholder={
                                          preference.direction ===
                                            'minimize'
                                            ? 'Lower is better'
                                            : 'Higher is better'
                                        }
                                      />
                                    </label>
                                  )
                                },
                              )}
                            </div>
                          )}

                        {preferences.length ===
                          0 && (
                            <div className="attribute-warning">
                              Add at least one
                              preference before
                              creating a decision.
                            </div>
                          )}
                      </div>
                    ),
                  )}
                </div>
              </div>

              {createDecisionError && (
                <div className="api-error modal-error">
                  <strong>
                    Unable to create decision
                  </strong>

                  <span>
                    {createDecisionError}
                  </span>
                </div>
              )}

              <div className="modal-footer">
                <button
                  type="button"
                  className="secondary-button"
                  onClick={
                    closeCreateDecisionModal
                  }
                  disabled={creatingDecision}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="primary-button"
                  disabled={
                    creatingDecision ||
                    preferences.length === 0
                  }
                >
                  {creatingDecision
                    ? 'Creating...'
                    : 'Create Decision'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default App