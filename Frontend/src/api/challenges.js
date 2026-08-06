import api from './axios'

export async function fetchChallenges(bustCache = false){
  // Add cache buster parameter to force fresh data when needed
  const params = bustCache ? { _t: Date.now() } : {}
  const res = await api.get('/challenges/', { params })
  return res.data
}

export async function fetchChallenge(slug){
  const res = await api.get(`/challenges/${slug}/`)
  return res.data
}

export async function submitAttempt(challengeId, payload, idempotencyKey){
  const headers = idempotencyKey ? { 'X-Idempotency-Key': idempotencyKey } : {}
  const res = await api.post(`/challenges/${challengeId}/submit/`, payload, { headers })
  return res.data
}

export async function fetchMySubmissions(challengeId){
  const res = await api.get(`/challenges/submissions/me/`, {
    params: challengeId ? { challenge_id: challengeId } : {}
  })
  return res.data
}

export async function fetchUserProfile(){
  const res = await api.get('/auth/profile/')
  return res.data
}

export async function fetchChallengeProgress(challengeId){
  const res = await api.get(`/challenges/${challengeId}/progress/`)
  return res.data
}

export async function fetchSubmissionById(submissionId){
  // Fetch a specific submission by submission ID with full graded results
  const res = await api.get(`/challenges/submissions/${submissionId}/`)
  return res.data
}
