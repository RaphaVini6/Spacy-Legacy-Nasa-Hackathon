// After a new deploy the old page chunks no longer exist, so a tab that was already open fails to
// load the next page. Reloading once fetches the new index.html and its new chunk names.
const KEY = 'reloaded-for'

export function reloadOnce() {
  try {
    if (sessionStorage.getItem(KEY) === location.pathname) return false
    sessionStorage.setItem(KEY, location.pathname)
  } catch {
    // storage blocked: reload anyway, the browser stops at the error screen if it happens again
  }
  window.location.reload()
  return true
}

export function clearReloadFlag() {
  try {
    sessionStorage.removeItem(KEY)
  } catch {
    // ignore
  }
}

export const isChunkError = (error) =>
  /dynamically imported module|Importing a module script failed|error loading dynamically imported module|Loading chunk/i.test(String(error?.message ?? error))

// lazy() that reloads the page once when the chunk is missing
export const lazyPage = (load) => () =>
  load().then((module) => {
    // no module means the vite:preloadError handler already started a reload
    if (!module) return new Promise(() => {})
    clearReloadFlag()
    return module
  }, (error) => {
    if (isChunkError(error) && reloadOnce()) return new Promise(() => {}) // wait for the reload
    throw error
  })
