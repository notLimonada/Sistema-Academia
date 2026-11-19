$(function () {
  // ---------- Tema claro/escuro ----------
  function rotuloTema(t) {
    $('#tema-toggle').text(t === 'dark' ? '☀️ Claro' : '🌙 Escuro');
  }
  rotuloTema($('html').attr('data-bs-theme'));
  $('#tema-toggle').on('click', function () {
    var novo = $('html').attr('data-bs-theme') === 'dark' ? 'light' : 'dark';
    $('html').attr('data-bs-theme', novo);
    try { localStorage.setItem('tema', novo); } catch (e) {}
    rotuloTema(novo);
  });

  // ---------- Máscaras de formulário ----------
  $('.mask-cpf').on('input', function () {
    var d = $(this).val().replace(/\D/g, '').slice(0, 11);
    d = d.replace(/(\d{3})(\d)/, '$1.$2')
         .replace(/(\d{3})(\d)/, '$1.$2')
         .replace(/(\d{3})(\d{1,2})$/, '$1-$2');
    $(this).val(d);
  });

  $('.mask-tel').on('input', function () {
    var d = $(this).val().replace(/\D/g, '').slice(0, 11);
    var corte = d.length > 10 ? 7 : 6;
    var out = d.length ? '(' + d.slice(0, 2) : '';
    if (d.length > 2) { out += ') ' + d.slice(2, corte); }
    if (d.length > corte) { out += '-' + d.slice(corte); }
    $(this).val(out);
  });

  // ---------- Inscrição em turma via AJAX ----------
  function aviso(texto, tipo) {
    var $a = $('<div class="alert alert-dismissible fade show" role="alert"></div>')
      .addClass('alert-' + tipo).text(texto)
      .append('<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fechar"></button>');
    $('#avisos').empty().append($a);
  }

  $('.btn-turma').on('click', function () {
    var $btn = $(this), $linha = $btn.closest('tr');
    $btn.prop('disabled', true);
    $.ajax({
      url: $btn.data('url'),
      method: 'POST',
      dataType: 'json',
      headers: { 'X-CSRFToken': $('meta[name="csrf-token"]').attr('content') }
    }).done(function (r) {
      $linha.find('.ocupadas').text(r.ocupadas);
      if (r.inscrito) {
        $btn.removeClass('btn-primary btn-secondary').addClass('btn-outline-danger').text('Cancelar inscrição');
        $btn.data('bloqueado', false);
      } else if (r.ocupadas >= r.vagas) {
        $btn.removeClass('btn-primary btn-outline-danger').addClass('btn-secondary').text('Lotada');
        $btn.data('bloqueado', true);
      } else {
        $btn.removeClass('btn-outline-danger btn-secondary').addClass('btn-primary').text('Inscrever-se');
        $btn.data('bloqueado', false);
      }
      aviso(r.msg, 'success');
    }).fail(function (xhr) {
      var msg = (xhr.responseJSON && xhr.responseJSON.msg) || 'Não foi possível concluir a ação. Tente novamente.';
      aviso(msg, 'danger');
    }).always(function () {
      $btn.prop('disabled', $btn.data('bloqueado') === true);
    });
  });
});
