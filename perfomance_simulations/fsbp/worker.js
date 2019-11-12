
const Cloudworker = require('../lib/cloudworker')
const { KeyValueStore } = require('../lib/kv')


const script = `
      addEventListener('fetch', event => {
   event.respondWith(handleRequest(event.request))
 })
  async function handleRequest(request) {
    const answer = request.headers.get("greeting") || "hello"  
    return new Response(answer + " world")
 }
    `

const server = new Cloudworker(script).listen(8080)

