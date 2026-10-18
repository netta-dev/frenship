import type { Register } from 'claude-code'

export const register: Register = on => {
  on('prompt.context', ($, e, next) =>
    next({ ...e, blocks: e.blocks.filter(b => b.name !== 'userEmail') }),
  )
}
