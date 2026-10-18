import { expect, test } from 'claude-code/testing'

const BLOCKS = [
  { name: 'claudeMd', text: 'rules' },
  { name: 'userEmail', text: 'someone@example.com' },
  { name: 'currentDate', text: '2026-10-13' },
]

test('drops the userEmail block and keeps the others in order', async ($, on) => {
  on('prompt.context', (_$, e) => ({ blocks: e.blocks }))
  const { blocks } = await $.prompt.context({ blocks: BLOCKS })
  expect(blocks.map(b => b.name)).toEqual(['claudeMd', 'currentDate'])
})
