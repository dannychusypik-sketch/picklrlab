import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'paddle',
  title: 'Paddle',
  type: 'document',
  fields: [
    defineField({
      name: 'brand',
      title: 'Brand',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'name',
      title: 'Name',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'slug',
      title: 'Slug',
      type: 'slug',
      options: { source: 'name', maxLength: 96 },
    }),
    defineField({
      name: 'priceUsd',
      title: 'Price (USD)',
      type: 'number',
    }),
    defineField({
      name: 'buyUrl',
      title: 'Buy URL',
      type: 'url',
    }),
    defineField({
      name: 'coreMm',
      title: 'Core (mm)',
      type: 'number',
    }),
    defineField({
      name: 'faceMaterial',
      title: 'Face Material',
      type: 'string',
    }),
    defineField({
      name: 'weightOz',
      title: 'Weight (oz)',
      type: 'number',
    }),
    defineField({
      name: 'scoreOverall',
      title: 'Score: Overall',
      type: 'number',
      validation: (Rule) => Rule.min(0).max(10),
    }),
    defineField({
      name: 'scoreControl',
      title: 'Score: Control',
      type: 'number',
      validation: (Rule) => Rule.min(0).max(10),
    }),
    defineField({
      name: 'scorePower',
      title: 'Score: Power',
      type: 'number',
      validation: (Rule) => Rule.min(0).max(10),
    }),
    defineField({
      name: 'scoreSpin',
      title: 'Score: Spin',
      type: 'number',
      validation: (Rule) => Rule.min(0).max(10),
    }),
    defineField({
      name: 'scoreDurability',
      title: 'Score: Durability',
      type: 'number',
      validation: (Rule) => Rule.min(0).max(10),
    }),
    defineField({
      name: 'scoreFeel',
      title: 'Score: Feel',
      type: 'number',
      validation: (Rule) => Rule.min(0).max(10),
    }),
    defineField({
      name: 'scoreValue',
      title: 'Score: Value',
      type: 'number',
      validation: (Rule) => Rule.min(0).max(10),
    }),
    defineField({
      name: 'verdict',
      title: 'Verdict',
      type: 'string',
    }),
    defineField({
      name: 'goodFor',
      title: 'Good For',
      type: 'array',
      of: [{ type: 'string' }],
    }),
    defineField({
      name: 'badFor',
      title: 'Bad For',
      type: 'array',
      of: [{ type: 'string' }],
    }),
    defineField({
      name: 'featured',
      title: 'Featured',
      type: 'boolean',
      initialValue: false,
    }),
    defineField({
      name: 'mainImage',
      title: 'Main Image',
      type: 'image',
    }),
  ],
})
