import { defineConfig } from 'sanity'
import { structureTool } from 'sanity/structure'
import { schemaTypes } from './schemas'

export default defineConfig({
  name: 'picklrlab',
  title: 'PicklrLab CMS',
  projectId: 'zy6ukasd',
  dataset: 'production',
  plugins: [structureTool()],
  schema: { types: schemaTypes },
})
