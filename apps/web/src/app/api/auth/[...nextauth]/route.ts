import NextAuth, { NextAuthOptions } from "next-auth"
import GoogleProvider from "next-auth/providers/google"

const authOptions: NextAuthOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID || "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
    }),
  ],
  callbacks: {
    async jwt({ token, account }) {
      // Upon initial sign in, swap Google ID token for CineRec API token
      if (account && account.id_token) {
        try {
          const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/login/google`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id_token: account.id_token })
          })
          
          if (res.ok) {
            const data = await res.json()
            token.accessToken = data.access_token
          }
        } catch (error) {
          console.error("Failed to swap token with backend API", error)
        }
      }
      return token
    },
    async session({ session, token }) {
      // Pass the access token to the client so it can authorize API requests
      session.accessToken = token.accessToken as string
      return session
    }
  },
  session: {
    strategy: "jwt",
  }
}

const handler = NextAuth(authOptions)

export { handler as GET, handler as POST }
