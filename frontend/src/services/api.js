
import axios from 'axios'

const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL ||
    'http://127.0.0.1:8000/api/v1'

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 30000,
})

export const healthCheck = async () => {
    const response = await axios.get(
        'http://127.0.0.1:8000/health',
    )

    return response.data
}

// Decisions

export const getUserDecisions = async (userId) => {
    const response = await api.get(
        `/decisions/user/${userId}`,
    )

    return response.data
}

export const getDecision = async (decisionId) => {
    const response = await api.get(
        `/decisions/${decisionId}`,
    )

    return response.data
}

export const createDecision = async (decisionData) => {
    const response = await api.post(
        '/decisions/',
        decisionData,
    )

    return response.data
}

export const evaluateDecision = async (decisionId) => {
    const response = await api.post(
        `/decisions/${decisionId}/evaluate`,
    )

    return response.data
}

// Preferences

export const getUserPreferences = async (userId) => {
    const response = await api.get(
        `/preferences/user/${userId}`,
    )

    return response.data
}

// Feedback

export const submitFeedback = async (feedbackData) => {
    const response = await api.post(
        '/feedback/',
        feedbackData,
    )

    return response.data
}

export const getDecisionFeedback = async (decisionId) => {
    const response = await api.get(
        `/feedback/decision/${decisionId}`,
    )

    return response.data
}

export const getUserFeedback = async (userId) => {
    const response = await api.get(
        `/feedback/user/${userId}`,
    )

    return response.data
}

// Learning engine

export const learnFromFeedback = async (feedbackId) => {
    const response = await api.post(
        `/learning/feedback/${feedbackId}`,
    )

    return response.data
}

export const getUserLearningHistory = async (userId) => {
    const response = await api.get(
        `/learning/history/user/${userId}`,
    )

    return response.data
}

export default api
