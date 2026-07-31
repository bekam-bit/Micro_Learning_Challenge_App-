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
