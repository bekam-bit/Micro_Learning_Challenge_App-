import api from './axios'

export async function fetchChallenges(){
  const res = await api.get('/challenges/')
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
  // This should fetch the full submission with results
  // We'll need to check if there's an endpoint for this
  const res = await api.get(`/challenges/submissions/${submissionId}/`)
  return res.data
}

export async function fetchChallengeSubmissionResult(challengeId){
  const res = await api.get(`/challenges/${challengeId}/result/`)
  return res.data
}
