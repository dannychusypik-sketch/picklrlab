import { createClient } from 'next-sanity'

export const sanityClient = createClient({
  projectId: 'zy6ukasd',
  dataset: 'production',
  apiVersion: '2024-01-01',
  useCdn: true,
})
