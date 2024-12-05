// Seletores para os elementos da interface
const calendar = document.querySelector(".calendar"),
      date = document.querySelector(".date"),
      daysContainer = document.querySelector(".days"),
      prev = document.querySelector(".prev"),
      next = document.querySelector(".next"),
      todayBtn = document.querySelector(".today-btn"),
      gotoBtn = document.querySelector(".goto-btn"),
      dateInput = document.querySelector(".date-input"),
      eventDay = document.querySelector(".event-day"),
      eventDate = document.querySelector(".event-date"),
      eventsContainer = document.querySelector(".events"),
      addEventBtn = document.querySelector(".add-event"),
      addEventWrapper = document.querySelector(".add-event-wrapper"),
      addEventCloseBtn = document.querySelector(".close"),
      addEventTitle = document.querySelector(".event-name"),
      addEventFrom = document.querySelector(".event-time-from"),
      addEventTo = document.querySelector(".event-time-to"),
      addEventSubmit = document.querySelector(".add-event-btn");

let today = new Date();
let activeDay;
let month = today.getMonth();
let year = today.getFullYear();
let selectedDate;

const months = [
  "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", 
  "Setembro", "Outubro", "Novembro", "Dezembro"
];

let eventArr = [];

// Função para buscar eventos do servidor
async function fetchEvents() {
  try {
    const response = await fetch('/get-events'); // Rota do Flask para retornar eventos
    if (response.ok) {
      eventArr = await response.json();
      console.log("Eventos carregados:", eventArr);
      initCalendar(); // Inicializa o calendário após carregar os eventos
    } else {
      console.error("Erro ao carregar eventos:", response.statusText);
    }
  } catch (error) {
    console.error("Erro ao buscar eventos:", error);
  }
}

// Chame a função de busca de eventos ao carregar a página
window.addEventListener('DOMContentLoaded', fetchEvents);

function initCalendar() {
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  const prevLastDay = new Date(year, month, 0);
  const prevDays = prevLastDay.getDate();
  const lastDate = lastDay.getDate();
  const day = firstDay.getDay();
  const nextDays = 7 - lastDay.getDay() - 1;

  date.innerHTML = months[month] + " " + year;

  let days = "";

  // Preencher os dias do mês anterior (para alinhar o início do mês corretamente)
  for (let x = day; x > 0; x--) {
    days += `<div class="day prev-date">${prevDays - x + 1}</div>`;
  }

  // Preencher os dias do mês atual
  for (let i = 1; i <= lastDate; i++) {
    let event = false;

    // Buscando eventos do servidor para o mês e dia
    eventArr.forEach((eventObj) => {
      if (eventObj.day === i && eventObj.month === month + 1 && eventObj.year === year) {
        event = true;
      }
    });

    if (i === new Date().getDate() && year === new Date().getFullYear() && month === new Date().getMonth()) {
      activeDay = i;
      getActiveDay(i);
      updateEvents(i);
      days += event ? `<div class="day today active event">${i}</div>` : `<div class="day today active">${i}</div>`;
    } else {
      days += event ? `<div class="day event">${i}</div>` : `<div class="day">${i}</div>`;
    }
  }

  // Preencher os dias do próximo mês
  for (let j = 1; j <= nextDays; j++) {
    days += `<div class="day next-date">${j}</div>`;
  }

  daysContainer.innerHTML = days;
  addListener();
}

initCalendar();

// Funções de navegação entre os meses
function prevMonth() {
  month--;
  if (month < 0) {
    month = 11;
    year--;
  }
  initCalendar();
  getActiveDay(activeDay);
  updateEvents(activeDay);
}

function nextMonth() {
  month++;
  if (month > 11) {
    month = 0;
    year++;
  }
  initCalendar();
  getActiveDay(activeDay);
  updateEvents(activeDay);
}

prev.addEventListener("click", prevMonth);
next.addEventListener("click", nextMonth);

todayBtn.addEventListener("click", () => {
  today = new Date();
  month = today.getMonth();
  year = today.getFullYear();
  initCalendar();
});

// Função de navegação para data específica (mm/yyyy)
dateInput.addEventListener("keyup", (e) => {
  dateInput.value = dateInput.value.replace(/[^0-9/]/g, "");
  if (dateInput.value.length === 2) {
    dateInput.value += "/";
  }
  if (dateInput.value.length > 7) {
    dateInput.value = dateInput.value.slice(0, 7);
  }
  if (e.inputType === "deleteContentBackward" && dateInput.value.length === 3) {
    dateInput.value = dateInput.value.slice(0, 2);
  }
});

gotoBtn.addEventListener("click", gotoDate);

function gotoDate() {
  const dateArr = dateInput.value.split("/");
  if (dateArr.length === 2) {
    let inputMonth = parseInt(dateArr[0], 10);
    let inputYear = parseInt(dateArr[1], 10);
    if (inputMonth > 0 && inputMonth <= 12 && inputYear.toString().length === 4) {
      month = inputMonth - 1;
      year = inputYear;
      initCalendar();
    } else {
      alert("Data inválida. Verifique o formato mm/yyyy.");
    }
  } else {
    alert("Data inválida. Use o formato mm/yyyy.");
  }
}

// Abertura e fechamento do painel de adicionar evento
addEventBtn.addEventListener("click", () => {
  addEventWrapper.classList.toggle('active');
});

addEventCloseBtn.addEventListener("click", () => {
  addEventWrapper.classList.remove('active');
});

// Fechar quando clicar fora do painel de adicionar evento
document.addEventListener('click', (e) => {
  if (!addEventWrapper.contains(e.target) && e.target !== addEventBtn) {
    addEventWrapper.classList.remove('active');
  }
});

// Limitar caracteres nos campos de nome de evento e horários
addEventTitle.addEventListener("input", () => {
  addEventTitle.value = addEventTitle.value.slice(0, 50);
});

addEventFrom.addEventListener("input", () => {
  addEventFrom.value = addEventFrom.value.replace(/[^0-9:]/g, "");
  if (addEventFrom.value.length === 2) {
    addEventFrom.value += ":";
  }
  if (addEventFrom.value.length > 5) {
    addEventFrom.value = addEventFrom.value.slice(0, 5);
  }
});

addEventTo.addEventListener("input", () => {
  addEventTo.value = addEventTo.value.replace(/[^0-9:]/g, "");
  if (addEventTo.value.length === 2) {
    addEventTo.value += ":";
  }
  if (addEventTo.value.length > 5) {
    addEventTo.value = addEventTo.value.slice(0, 5);
  }
});

function addListener() {
  const days = document.querySelectorAll(".day");
  days.forEach((day) => {
    day.addEventListener("click", (e) => {
      activeDay = Number(e.target.innerHTML);
      // Atualiza selectedDate com a data selecionada pelo usuário
      selectedDate = `${year}-${String(month + 1).padStart(2, '0')}-${String(activeDay).padStart(2, '0')}`;
      days.forEach((day) => day.classList.remove("active"));
      e.target.classList.add("active");
      updateEvents(activeDay);
    });
  });
}

function getActiveDay(date) {
  const day = new Date(year, month, date);
  const dayName = day.toLocaleDateString('pt-BR', { weekday: 'short' });
  eventDay.innerHTML = dayName;
  eventDate.innerHTML = date + " " + months[month] + " " + year;
  addEventBtn.classList.add('visible');  // Torna o botão de adicionar evento visível
}

function updateEvents(date) {
  let events = "";
  eventArr.forEach((event) => {
    if (date === event.day && month + 1 === event.month && year === event.year) {
      event.events.forEach((event) => {
        const aspirantes = event.aspirantes.join(", "); // Lista de aspirantes
        events += `<div class="event">
          <div class="title">
            <i class="fas fa-circle"></i>${event.title}
          </div>
          <div class="aspirantes">Aspirantes: ${aspirantes}</div>
          <div class="time">${event.time}</div>
        </div>`;
      });
    }
  });
  eventsContainer.innerHTML = events;
}

// Enviar dados de evento para o servidor
addEventSubmit.addEventListener("click", () => {
  // Construa a data no formato desejado (com "th" e o nome completo do mês)
  const day = String(activeDay).padStart(2, '0'); // Garantir que o dia tenha dois dígitos
  const date = new Date(year, month, activeDay);
  const dayName = date.toLocaleDateString('pt-BR', { day: 'numeric', month: 'long', year: 'numeric' });
  
  const formattedDate = `${day}th ${date.toLocaleString('pt-BR', { month: 'long' })} ${year}`;

  const event = {
    title: addEventTitle.value,
    date: formattedDate, // Formato '12th Novembro 2024'
    time: `${addEventFrom.value} - ${addEventTo.value}`,
    aspirants: [] // Preenchido com aspirantes selecionados
  };

  console.log("Dados enviados para o evento:", event);

  fetch('/add-event', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(event),
  })
  .then(response => response.json())
  .then(data => {
    alert("Evento criado com sucesso!");
    addEventWrapper.classList.remove('active');
    initCalendar(); // Atualize o calendário
  })
  .catch((error) => {
    console.error("Erro ao adicionar evento:", error);
  });
});