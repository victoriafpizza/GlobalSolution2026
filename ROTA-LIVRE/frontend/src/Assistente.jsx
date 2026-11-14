import { useState } from 'react'

export default function Assistente() {
  const [pergunta, setPergunta] = useState('')
  const [resposta, setResposta] = useState(null)
  const [erro, setErro] = useState('')
  const [ocupado, setOcupado] = useState(false)

  async function enviar(evento) {
    evento.preventDefault()
    if (!pergunta.trim() || ocupado) return
    setOcupado(true)
    setErro('')
    setResposta(null)
    try {
      const retorno = await fetch('/api/ai/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pergunta }),
        signal: AbortSignal.timeout(45000),
      })
      if (!retorno.ok) throw new Error()
      setResposta(await retorno.json())
    } catch {
      setErro('O assistente está indisponível. Tente novamente.')
    } finally {
      setOcupado(false)
    }
  }

  return (
    <section aria-labelledby="titulo-assistente" style={{ padding: '1rem' }}>
      <h2 id="titulo-assistente">Assistente de acessibilidade</h2>
      <form onSubmit={enviar}>
        <label htmlFor="pergunta-ai">Pergunta sobre acessibilidade urbana</label>
        <p>Evite incluir dados pessoais.</p>
        <textarea id="pergunta-ai" value={pergunta} maxLength={600} required
          onChange={(evento) => setPergunta(evento.target.value)} />
        <button type="submit" disabled={ocupado || !pergunta.trim()}>Enviar</button>
      </form>
      <div aria-live="polite">
        {ocupado && <p>Consultando a base documental…</p>}
        {erro && <p role="alert">{erro}</p>}
        {resposta && <><p>{resposta.resposta}</p>
          {resposta.citacoes.length > 0 && <ul>{resposta.citacoes.map((fonte) =>
            <li key={fonte.chunk_id}><a href={fonte.url}>{fonte.titulo}</a></li>
          )}</ul>}
        </>}
      </div>
    </section>
  )
}
