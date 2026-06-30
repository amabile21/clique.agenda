const estado = {
  visaoAtual: 'inicio',
  dataSelecionada: new Date(),
  escalaFonte: 1,
  listaContatos: [],
  tipoPesquisaAtiva: '',
  termoPesquisaAtiva: '',
  tipoItemFormulario: 'lembrete',
  itemSendoEditado: null
};

let callbackConfirmacao = null;

const nomesMeses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
const diasDaSemana = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];

const htmlRaiz = document.documentElement;
const listaLembretes = document.getElementById('lista-lembretes');
const listaCompromissos = document.getElementById('lista-compromissos');
const tituloVisao = document.getElementById('titulo-visao');
const containerAdicionarInicio = document.getElementById('container-adicionar-inicio');
const inputPesquisaContato = document.getElementById('input-pesquisa-contato');
const inputPesquisaTitulo = document.getElementById('input-pesquisa-titulo');
const listaContratosFrequentes = document.getElementById('lista-sugestoes-contato');
const itensSugestoesContato = document.getElementById('itens-sugestoes-contato');
const btnDiminuirFonte = document.getElementById('btn-diminuir-fonte');
const btnAumentarFonte = document.getElementById('btn-aumentar-fonte');
const btnAbrirModalAdicionar = document.getElementById('btn-abrir-modal-adicionar');

const modalItem = document.getElementById('modal-item');
const tituloModalItem = document.getElementById('titulo-modal-item');
const abasModalItem = document.getElementById('abas-modal-item');
const formularioItem = document.getElementById('formulario-item');
const idItem = document.getElementById('id-item');
const tituloItem = document.getElementById('titulo-item');
const camposCompromisso = document.getElementById('campos-compromisso');
const contatoItem = document.getElementById('contato-item');
const dataItem = document.getElementById('data-item');
const horaItem = document.getElementById('hora-item');
const observacaoItem = document.getElementById('observacao-item');

const modalContato = document.getElementById('modal-contato');
const tituloModalContato = document.getElementById('titulo-modal-contato');
const formularioContato = document.getElementById('formulario-contato');
const idContato = document.getElementById('id-contato');
const nomeContato = document.getElementById('nome-contato');
const telefoneContato = document.getElementById('telefone-contato');
const emailContato = document.getElementById('email-contato');

const modalConfirmacao = document.getElementById('modal-confirmacao');
const tituloConfirmacao = document.getElementById('titulo-confirmacao');
const mensagemConfirmacao = document.getElementById('mensagem-confirmacao');

document.addEventListener('DOMContentLoaded', () => {
  carregarConfiguracoes();
  configurarEventos();
  
  if (window.pywebview) {
    window.pywebview.api.inicializar_banco().then(() => {
      atualizarCacheContatos();
      renderizarVisaoAtual();
    });
  } else {
    window.addEventListener('pywebviewready', () => {
      window.pywebview.api.inicializar_banco().then(() => {
        atualizarCacheContatos();
        renderizarVisaoAtual();
      });
    });
  }
});

function carregarConfiguracoes() {
  const escala = parseInt(localStorage.getItem('agendai-escala-fonte') || '1', 10);
  estado.escalaFonte = escala;
  htmlRaiz.dataset.escalaFonte = escala;
}

function salvarConfiguracoes() {
  localStorage.setItem('agendai-escala-fonte', estado.escalaFonte);
}

function configurarEventos() {
  document.getElementById('logo').addEventListener('click', () => alternarVisao('inicio'));
  document.getElementById('link-hoje').addEventListener('click', () => alternarVisao('inicio'));
  document.getElementById('link-esta-semana').addEventListener('click', () => alternarVisao('semana'));
  document.getElementById('link-este-mes').addEventListener('click', () => alternarVisao('mes'));
  document.getElementById('link-90-dias').addEventListener('click', () => alternarVisao('90dias'));
  document.getElementById('link-adicionar-contato').addEventListener('click', () => abrirModalContato());
  document.getElementById('link-ver-contatos').addEventListener('click', () => alternarVisao('contatos'));

  btnDiminuirFonte.addEventListener('click', () => {
    if (estado.escalaFonte > 1) {
      estado.escalaFonte--;
      htmlRaiz.dataset.escalaFonte = estado.escalaFonte;
      salvarConfiguracoes();
    }
  });

  btnAumentarFonte.addEventListener('click', () => {
    if (estado.escalaFonte < 4) {
      estado.escalaFonte++;
      htmlRaiz.dataset.escalaFonte = estado.escalaFonte;
      salvarConfiguracoes();
    }
  });

  btnAbrirModalAdicionar.addEventListener('click', () => abrirModalItem());

  inputPesquisaTitulo.addEventListener('input', () => {
    if (inputPesquisaTitulo.value.trim()) {
      estado.tipoPesquisaAtiva = 'titulo';
      estado.termoPesquisaAtiva = inputPesquisaTitulo.value;
      alternarVisao('pesquisa');
    } else {
      alternarVisao('inicio');
    }
  });

  inputPesquisaContato.addEventListener('focus', mostrarSugestoesContatos);
  inputPesquisaContato.addEventListener('input', () => {
    if (inputPesquisaContato.value.trim()) {
      estado.tipoPesquisaAtiva = 'contato';
      estado.termoPesquisaAtiva = inputPesquisaContato.value;
      alternarVisao('pesquisa');
    } else {
      alternarVisao('inicio');
    }
    mostrarSugestoesContatos();
  });

  document.addEventListener('click', e => {
    if (!inputPesquisaContato.contains(e.target) && !listaContratosFrequentes.contains(e.target)) {
      listaContratosFrequentes.classList.remove('visivel');
    }
  });

  abasModalItem.querySelectorAll('.botao-aba').forEach(btn => {
    btn.addEventListener('click', () => definirTipoFormularioModal(btn.dataset.tipo));
  });

  document.getElementById('btn-fechar-modal-item').addEventListener('click', fecharModalItem);
  document.getElementById('btn-cancelar-modal-item').addEventListener('click', fecharModalItem);
  document.getElementById('btn-fechar-modal-contato').addEventListener('click', fecharModalContato);
  document.getElementById('btn-cancelar-modal-contato').addEventListener('click', fecharModalContato);
  document.getElementById('btn-confirmar-nao').addEventListener('click', fecharModalConfirmacao);
  
  document.getElementById('btn-confirmar-sim').addEventListener('click', () => {
    if (callbackConfirmacao) callbackConfirmacao();
    fecharModalConfirmacao();
  });

  formularioItem.addEventListener('submit', enviarFormularioItem);
  formularioContato.addEventListener('submit', enviarFormularioContato);
}

function alternarVisao(novaVisao) {
  estado.visaoAtual = novaVisao;
  if (novaVisao !== 'pesquisa') {
    estado.tipoPesquisaAtiva = '';
    estado.termoPesquisaAtiva = '';
  }
  renderizarVisaoAtual();
}

function renderizarVisaoAtual() {
  listaLembretes.innerHTML = '';
  listaCompromissos.innerHTML = '';
  containerAdicionarInicio.style.display = estado.visaoAtual === 'inicio' ? 'flex' : 'none';

  if (!window.pywebview || !window.pywebview.api) return;

  switch (estado.visaoAtual) {
    case 'inicio':
      tituloVisao.textContent = formatarDataExibicao(estado.dataSelecionada);
      window.pywebview.api.obter_agenda(formatarDataISO(estado.dataSelecionada)).then(renderizarAgendaDiaria);
      break;
    case 'semana':
    case 'mes':
    case '90dias':
      const rotulos = { semana: 'Esta Semana', mes: 'Este Mês', '90dias': 'Próximos 90 dias' };
      tituloVisao.textContent = rotulos[estado.visaoAtual];
      const hoje = new Date();
      const diasFim = estado.visaoAtual === 'semana' ? 6 : estado.visaoAtual === 'mes' ? 29 : 89;
      window.pywebview.api.obter_agenda_periodo(formatarDataISO(hoje), formatarDataISO(adicionarDias(hoje, diasFim))).then(renderizarCalendarioPeriodo);
      break;
    case 'pesquisa':
      tituloVisao.textContent = `Pesquisa: "${estado.termoPesquisaAtiva}"`;
      window.pywebview.api.pesquisar_compromissos(estado.tipoPesquisaAtiva, estado.termoPesquisaAtiva).then(renderizarResultadosPesquisa);
      break;
    case 'contatos':
      tituloVisao.textContent = 'Contatos';
      renderizarVisaoContatos();
      break;
  }
}

function renderizarAgendaDiaria(dados) {
  const lembretes = dados.lembretes || [];
  const compromissos = dados.compromissos || [];
  if (lembretes.length === 0 && compromissos.length === 0) {
    listaCompromissos.innerHTML = '<div class="estado-vazio">Nada para hoje.</div>';
    return;
  }
  compromissos.forEach(c => listaCompromissos.appendChild(criarCartaoCompromisso(c)));
  lembretes.forEach(l => listaLembretes.appendChild(criarCartaoLembrete(l)));
}

function renderizarCalendarioPeriodo(dados) {
  const compromissos = dados.compromissos || [];
  const hoje = new Date();
  const containerCal = document.createElement('div');
  containerCal.className = 'container-calendario';

  if (estado.visaoAtual === 'semana') {
    const domingo = new Date(hoje);
    domingo.setDate(hoje.getDate() - hoje.getDay());
    const dias = [];
    for (let i = 0; i < 7; i++) {
      const d = new Date(domingo);
      d.setDate(domingo.getDate() + i);
      const dataStr = formatarDataISO(d);
      dias.push({ dataStr, numeroDia: d.getDate(), ehHoje: dataStr === formatarDataISO(hoje), eventos: compromissos.filter(e => e.data === dataStr) });
    }
    containerCal.appendChild(construirCalendario(`Semana de ${formatarDataExibicao(domingo)}`, dias));
  } else if (estado.visaoAtual === 'mes') {
    const dias = gerarGradeMes(hoje.getFullYear(), hoje.getMonth(), compromissos, hoje);
    containerCal.appendChild(construirCalendario(`${nomesMeses[hoje.getMonth()]} ${hoje.getFullYear()}`, dias));
  } else if (estado.visaoAtual === '90dias') {
    for (let i = 0; i < 3; i++) {
      let m = hoje.getMonth() + i;
      let a = hoje.getFullYear();
      if (m > 11) { m -= 12; a += 1; }
      const dias = gerarGradeMes(a, m, compromissos, hoje);
      containerCal.appendChild(construirCalendario(`${nomesMeses[m]} ${a}`, dias));
    }
  }
  listaCompromissos.appendChild(containerCal);
}

function gerarGradeMes(ano, mes, compromissos, hoje) {
  const primeiroDia = new Date(ano, mes, 1).getDay();
  const totalDias = new Date(ano, mes + 1, 0).getDate();
  const dias = [];
  for (let i = 0; i < primeiroDia; i++) dias.push({ vazio: true });
  for (let d = 1; d <= totalDias; d++) {
    const dObj = new Date(ano, mes, d);
    const dataStr = formatarDataISO(dObj);
    dias.push({ dataStr, numeroDia: d, ehHoje: dataStr === formatarDataISO(hoje), eventos: compromissos.filter(e => e.data === dataStr) });
  }
  return dias;
}

function construirCalendario(titulo, dias) {
  const div = document.createElement('div');
  div.innerHTML = `<div class="titulo-calendario">${titulo}</div>`;
  const tabela = document.createElement('table');
  tabela.className = 'tabela-calendario';
  tabela.innerHTML = `<thead><tr>${diasDaSemana.map(d => `<th>${d}</th>`).join('')}</tr></thead>`;
  const tbody = document.createElement('tbody');
  let tr = document.createElement('tr');
  dias.forEach((d, idx) => {
    if (idx > 0 && idx % 7 === 0) {
      tbody.appendChild(tr);
      tr = document.createElement('tr');
    }
    const td = document.createElement('td');
    if (d.vazio) {
      td.className = 'dia-vazio';
    } else {
      if (d.ehHoje) td.classList.add('dia-hoje');
      let eventosHtml = (d.eventos || []).map(e => `<div class="titulo-evento-dia" title="${e.titulo}">${e.hora} - ${e.titulo}</div>`).join('');
      td.innerHTML = `<div class="numero-dia">${d.numeroDia}</div><div class="eventos-do-dia">${eventosHtml}</div>`;
    }
    tr.appendChild(td);
  });
  tbody.appendChild(tr);
  tabela.appendChild(tbody);
  div.appendChild(tabela);
  return div;
}

function renderizarResultadosPesquisa(dados) {
  const compromissos = dados.compromissos || [];
  if (compromissos.length === 0) {
    listaCompromissos.innerHTML = '<div class="estado-vazio">Nenhum compromisso encontrado.</div>';
    return;
  }
  compromissos.forEach(c => listaCompromissos.appendChild(criarCartaoCompromisso(c, true)));
}

function renderizarVisaoContatos() {
  listaCompromissos.innerHTML = `
    <div class="barra-pesquisa-contato"><input type="text" id="pesquisa-contato-interno" placeholder="Filtrar contatos..."></div>
    <div class="grade-contatos" id="lista-contatos-interna"></div>`;
  const listaInterna = document.getElementById('lista-contatos-interna');
  
  const carregar = (termo = '') => {
    listaInterna.innerHTML = '<div class="estado-vazio">Carregando...</div>';
    const acao = termo.trim() ? window.pywebview.api.pesquisar_contatos(termo) : window.pywebview.api.obter_contatos();
    acao.then(contatos => {
      listaInterna.innerHTML = contatos.length === 0 ? '<div class="estado-vazio">Nenhum contato encontrado.</div>' : '';
      contatos.forEach(c => listaInterna.appendChild(criarItemContato(c)));
    });
  };
  carregar();
  document.getElementById('pesquisa-contato-interno').addEventListener('input', e => carregar(e.target.value));
}

function criarCartaoLembrete(l) {
  const clone = document.getElementById('template-cartao-lembrete').content.cloneNode(true);
  const cartao = clone.querySelector('.cartao');
  if (l.concluido) cartao.classList.add('concluido');
  clone.querySelector('.circulo-conclusao').addEventListener('click', () => {
    window.pywebview.api.concluir_lembrete(l.id, !l.concluido).then(() => renderizarVisaoAtual());
  });
  clone.querySelector('.titulo-cartao').textContent = l.titulo;
  if (l.observacao) {
    const obs = clone.querySelector('.observacao-cartao');
    obs.textContent = l.observacao;
    obs.removeAttribute('hidden');
  }
  clone.querySelector('.acao-editar').addEventListener('click', () => abrirModalItem(l, 'lembrete'));
  clone.querySelector('.acao-apagar').addEventListener('click', () => {
    exibirConfirmacao('Excluir Lembrete', 'Deseja excluir este lembrete?', () => {
      window.pywebview.api.excluir_lembrete(l.id).then(() => renderizarVisaoAtual());
    });
  });
  return clone;
}

function criarCartaoCompromisso(c, exibirData = false) {
  const clone = document.getElementById('template-cartao-compromisso').content.cloneNode(true);
  const cartao = clone.querySelector('.cartao');
  if (c.concluido) cartao.classList.add('concluido');
  clone.querySelector('.circulo-conclusao').addEventListener('click', () => {
    window.pywebview.api.concluir_compromisso(c.id, !c.concluido).then(() => renderizarVisaoAtual());
  });
  clone.querySelector('.titulo-cartao').textContent = c.titulo;
  clone.querySelector('.valor-hora').textContent = c.hora;
  if (exibirData) {
    const mData = clone.querySelector('.meta-data');
    mData.removeAttribute('hidden');
    clone.querySelector('.valor-data').textContent = formatarStringDataExibicao(c.data);
  }
  if (c.contato_nome) {
    const mCont = clone.querySelector('.meta-contato');
    mCont.removeAttribute('hidden');
    clone.querySelector('.valor-contato').textContent = c.contato_nome;
  }
  if (c.observacao) {
    const obs = clone.querySelector('.observacao-cartao');
    obs.textContent = c.observacao;
    obs.removeAttribute('hidden');
  }
  clone.querySelector('.acao-editar').addEventListener('click', () => {
    window.pywebview.api.obter_compromisso(c.id).then(completo => abrirModalItem(completo, 'compromisso'));
  });
  clone.querySelector('.acao-apagar').addEventListener('click', () => {
    exibirConfirmacao('Excluir Compromisso', 'Deseja excluir este compromisso?', () => {
      window.pywebview.api.excluir_compromisso(c.id).then(() => renderizarVisaoAtual());
    });
  });
  return clone;
}

function criarItemContato(c) {
  const clone = document.getElementById('template-item-contato').content.cloneNode(true);
  clone.querySelector('.nome-contato').textContent = c.nome;
  if (c.telefone) {
    const dt = clone.querySelector('.detalhe-telefone');
    dt.removeAttribute('hidden');
    clone.querySelector('.valor-telefone').textContent = c.telefone;
  }
  if (c.email) {
    const de = clone.querySelector('.detalhe-email');
    de.removeAttribute('hidden');
    clone.querySelector('.valor-email').textContent = c.email;
  }
  clone.querySelector('.acao-editar-contato').addEventListener('click', () => abrirModalContato(c));
  clone.querySelector('.acao-apagar-contato').addEventListener('click', () => {
    exibirConfirmacao('Excluir Contato', `Deseja excluir o contato ${c.nome}?`, () => {
      window.pywebview.api.excluir_contato(c.id).then(() => {
        atualizarCacheContatos();
        renderizarVisaoAtual();
      });
    });
  });
  return clone;
}

function atualizarCacheContatos() {
  window.pywebview.api.obter_contatos().then(contatos => {
    estado.listaContatos = contatos;
    contatoItem.innerHTML = '<option value="">Nenhum</option>';
    contatos.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c.id;
      opt.textContent = c.nome;
      contatoItem.appendChild(opt);
    });
  });
}

function mostrarSugestoesContatos() {
  window.pywebview.api.obter_contatos_frequentes().then(frequentes => {
    itensSugestoesContato.innerHTML = '';
    if (frequentes.length === 0) {
      listaContratosFrequentes.classList.remove('visivel');
      return;
    }
    frequentes.forEach(c => {
      const item = document.createElement('div');
      item.className = 'item-sugestao';
      item.textContent = c.nome;
      item.addEventListener('click', () => {
        inputPesquisaContato.value = c.nome;
        listaContratosFrequentes.classList.remove('visivel');
        estado.tipoPesquisaAtiva = 'contato';
        estado.termoPesquisaAtiva = c.nome;
        alternarVisao('pesquisa');
      });
      itensSugestoesContato.appendChild(item);
    });
    listaContratosFrequentes.classList.add('visivel');
  });
}

function abrirModalItem(item = null, tipoForçado = null) {
  formularioItem.reset();
  idItem.value = item ? item.id : '';
  
  if (item) {
    tituloModalItem.textContent = 'Editar Item';
    tituloItem.value = item.titulo || '';
    observacaoItem.value = item.observacao || '';
    const tipo = tipoForçado || (item.data ? 'compromisso' : 'lembrete');
    definirTipoFormularioModal(tipo);
    abasModalItem.style.display = 'none';

    if (tipo === 'compromisso') {
      contatoItem.value = item.contato_id || '';
      dataItem.value = item.data || '';
      horaItem.value = item.hora || '';
    }
    estado.itemSendoEditado = item;
  } else {
    tituloModalItem.textContent = 'Novo Item';
    definirTipoFormularioModal('lembrete');
    abasModalItem.style.display = 'flex';
    dataItem.value = formatarDataISO(estado.dataSelecionada);
    horaItem.value = '12:00';
    estado.itemSendoEditado = null;
  }
  modalItem.classList.add('visivel');
}

function fecharModalItem() { modalItem.classList.remove('visivel'); }

function definirTipoFormularioModal(tipo) {
  estado.tipoItemFormulario = tipo;
  abasModalItem.querySelectorAll('.botao-aba').forEach(btn => {
    btn.classList.toggle('ativa', btn.dataset.tipo === tipo);
  });
  if (tipo === 'compromisso') {
    camposCompromisso.removeAttribute('hidden');
    dataItem.required = true;
    horaItem.required = true;
  } else {
    camposCompromisso.setAttribute('hidden', 'true');
    dataItem.required = false;
    horaItem.required = false;
  }
}

function enviarFormularioItem(e) {
  e.preventDefault();
  const id = idItem.value;
  const titulo = tituloItem.value.trim();
  const obs = observacaoItem.value.trim();

  if (estado.tipoItemFormulario === 'lembrete') {
    if (id) {
      window.pywebview.api.atualizar_lembrete(parseInt(id, 10), titulo, obs, estado.itemSendoEditado.concluido).then(res => {
        if (res.sucesso) { fecharModalItem(); renderizarVisaoAtual(); }
      });
    } else {
      window.pywebview.api.adicionar_lembrete(titulo, obs).then(res => {
        if (res.sucesso) { fecharModalItem(); renderizarVisaoAtual(); }
      });
    }
  } else {
    const contatoId = contatoItem.value ? parseInt(contatoItem.value, 10) : null;
    const data = dataItem.value;
    const hora = horaItem.value;

    if (id) {
      window.pywebview.api.atualizar_compromisso(parseInt(id, 10), titulo, obs, data, hora, contatoId, estado.itemSendoEditado.concluido).then(res => {
        if (res.sucesso) { fecharModalItem(); renderizarVisaoAtual(); }
      });
    } else {
      window.pywebview.api.adicionar_compromisso(titulo, obs, data, hora, contatoId).then(res => {
        if (res.sucesso) { fecharModalItem(); renderizarVisaoAtual(); }
      });
    }
  }
}

function abrirModalContato(contato = null) {
  formularioContato.reset();
  if (contato) {
    tituloModalContato.textContent = 'Editar Contato';
    idContato.value = contato.id;
    nomeContato.value = contato.nome;
    telefoneContato.value = contato.telefone || '';
    emailContato.value = contato.email || '';
  } else {
    tituloModalContato.textContent = 'Novo Contato';
    idContato.value = '';
  }
  modalContato.classList.add('visivel');
}

function fecharModalContato() { modalContato.classList.remove('visivel'); }

function enviarFormularioContato(e) {
  e.preventDefault();
  const id = idContato.value;
  const nome = nomeContato.value.trim();
  const tel = telefoneContato.value.trim();
  const email = emailContato.value.trim();

  const acao = id ? window.pywebview.api.atualizar_contato(parseInt(id, 10), nome, tel, email) : window.pywebview.api.adicionar_contato(nome, tel, email);
  acao.then(res => {
    if (res.sucesso) {
      fecharModalContato();
      atualizarCacheContatos();
      renderizarVisaoAtual();
    }
  });
}

function exibirConfirmacao(titulo, mensagem, callback) {
  tituloConfirmacao.textContent = titulo;
  mensagemConfirmacao.textContent = mensagem;
  callbackConfirmacao = callback;
  modalConfirmacao.classList.add('visivel');
}

function fecharModalConfirmacao() { modalConfirmacao.classList.remove('visivel'); callbackConfirmacao = null; }

function formatarDataISO(data) { return data.toISOString().split('T')[0]; }

function formatarDataExibicao(data) {
  return `${diasDaSemana[data.getDay()]}, ${data.getDate()} de ${nomesMeses[data.getMonth()]}`;
}

function formatarStringDataExibicao(dataStr) {
  if (!dataStr) return '';
  const p = dataStr.split('-');
  return `${p[2]}/${p[1]}/${p[0]}`;
}

function adicionarDias(data, dias) {
  const nova = new Date(data);
  nova.setDate(nova.getDate() + dias);
  return nova;
}