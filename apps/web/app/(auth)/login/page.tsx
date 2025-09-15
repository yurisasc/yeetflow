import { redirect } from 'next/navigation'

export default function LoginPage() {
  // TODO: Implement authentication with better-auth
  // For now, redirect to flows page
  redirect('/flows')

  return null
}
