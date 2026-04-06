import { NextResponse } from 'next/server'
import { revalidatePath } from 'next/cache'

export async function POST(req: Request) {
  const { path, secret } = await req.json()
  if (secret !== process.env.SUPABASE_SERVICE_ROLE_KEY) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }
  revalidatePath(path || '/')
  return NextResponse.json({ revalidated: true })
}
