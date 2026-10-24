// ============ 0. SCROLL REVEAL ============
document.documentElement.classList.add("js");

const revealEls = document.querySelectorAll(".reveal");

if ("IntersectionObserver" in window) {
  const observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add("show");
        observer.unobserve(entry.target);    // animate only once
      }
    });
  }, { threshold: 0.15 });

  revealEls.forEach(function (el) { observer.observe(el); });
} else {
  revealEls.forEach(function (el) { el.classList.add("show"); });
}


// ============ 1. PROFILE DROPDOWN ============
const profileBtn = document.getElementById("profileBtn");
const profileMenu = document.getElementById("profileMenu");

profileBtn.addEventListener("click", function (event) {
  event.stopPropagation();               // stops this click from reaching the document below
  profileMenu.classList.toggle("open");  // add "open" if missing, remove it if present
});

// clicking anywhere else closes the menu
document.addEventListener("click", function () {
  profileMenu.classList.remove("open");
});

// pressing Escape closes it too
document.addEventListener("keydown", function (event) {
  if (event.key === "Escape") {
    profileMenu.classList.remove("open");
  }
});


// ============ 2. SWAP CARD (chips + swap button) ============
const HERO_SKILLS = ["Python", "Web Development", "Communication", "Football", "Graphic Design"];
const swapState = { teach: "Python", learn: "Communication" };

const swapBtn = document.getElementById("swapBtn");
const swapSides = document.querySelectorAll(".swap-side");
const teachName = document.querySelector(".teach strong");
const learnName = document.querySelector(".learn strong");
const teachChips = document.getElementById("teachChips");
const learnChips = document.getElementById("learnChips");
const swapNote = document.getElementById("swapNote");
let swapping = false;

// builds one row of chips; "key" is either "teach" or "learn"
function buildChips(container, key) {
  container.innerHTML = "";
  HERO_SKILLS.forEach(function (skill) {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "chip";
    chip.textContent = skill;
    chip.setAttribute("aria-pressed", swapState[key] === skill);

    chip.addEventListener("click", function () {
      swapState[key] = skill;
      renderSwap();
      if (swapState.teach === swapState.learn) {
        swapNote.textContent = "Choose two different skills to swap.";
      } else {
        swapNote.textContent = "Ready. Press the swap button.";
      }
    });

    container.appendChild(chip);
  });
}

// shows the current choices on the two cards and redraws the chips
function renderSwap() {
  teachName.textContent = swapState.teach;
  learnName.textContent = swapState.learn;
  buildChips(teachChips, "teach");
  buildChips(learnChips, "learn");
}

renderSwap();

swapBtn.addEventListener("click", function () {
  if (swapping) return;                  // ignore clicks while the animation is running

  if (swapState.teach === swapState.learn) {
    swapNote.textContent = "Choose two different skills to swap.";
    return;
  }

  swapping = true;

  swapSides.forEach(function (side) {
    side.classList.add("swap-pop");      // start the shrink-and-fade animation
  });

  // halfway through the animation, swap the two skills
  setTimeout(function () {
    const temp = swapState.teach;
    swapState.teach = swapState.learn;
    swapState.learn = temp;
    renderSwap();
  }, 250);

  // when the animation ends, clean up
  setTimeout(function () {
    swapSides.forEach(function (side) {
      side.classList.remove("swap-pop");
    });
    swapping = false;
    swapNote.textContent = "Swapped. Now you teach " + swapState.teach + " and learn " + swapState.learn + ". Balance stays at 400 SkillPoints.";
  }, 500);
});


// ============ 3. SWIPE FEEDBACK CARDS ============
const deck = document.getElementById("deck");
const tally = document.getElementById("tally");
const swipeMsg = document.getElementById("swipeMsg");   // CHANGED: new message line
const yesBtn = document.getElementById("yesBtn");
const noBtn = document.getElementById("noBtn");

const initialDeck = deck.innerHTML;      // remember the cards so "Start again" can restore them
let helpful = 0;
let notHelpful = 0;
let busy = false;                        // true while a card is flying away

function updateTally() {
  tally.textContent = helpful + " helpful · " + notHelpful + " not helpful";
}

// the card on top is the LAST .profile-card in the deck
function topCard() {
  const cards = deck.querySelectorAll(".profile-card");
  return cards[cards.length - 1] || null;
}

// direction: 1 = right (helpful), -1 = left (not helpful)
function fling(direction) {
  const card = topCard();
  if (!card || busy) return;
  busy = true;

  // CHANGED: the card slides away first and fades a little later, so the stamp stays visible
  card.classList.remove("dragging");
  card.style.transition = "transform 0.4s ease, opacity 0.25s ease 0.15s";
  card.style.transform = "translateX(" + direction * 500 + "px) rotate(" + direction * 25 + "deg)";
  card.style.opacity = "0";

  const stamp = card.querySelector(direction > 0 ? ".stamp-yes" : ".stamp-no");
  stamp.style.opacity = "1";

  // CHANGED: say what just happened
  const name = card.querySelector("h3").textContent;
  swipeMsg.textContent = name + (direction > 0 ? " marked as helpful" : " marked as not helpful");
  swipeMsg.className = "swipe-msg " + (direction > 0 ? "yes" : "no");

  if (direction > 0) {
    helpful++;
  } else {
    notHelpful++;
  }
  updateTally();

  setTimeout(function () {
    card.remove();                       // delete the card from the page
    busy = false;
    if (!topCard()) {
      document.getElementById("deckDone").style.display = "flex";   // show "All rated"
    }
  }, 400);
}

// buttons
yesBtn.addEventListener("click", function () { fling(1); });
noBtn.addEventListener("click", function () { fling(-1); });

// keyboard: click the deck once, then use the arrow keys
deck.setAttribute("tabindex", "0");
deck.addEventListener("keydown", function (event) {
  if (event.key === "ArrowRight") { event.preventDefault(); fling(1); }
  if (event.key === "ArrowLeft")  { event.preventDefault(); fling(-1); }
});

// dragging with mouse or finger
let startX = 0;
let dragX = 0;
let dragging = false;
let activeCard = null;

deck.addEventListener("pointerdown", function (event) {
  const card = event.target.closest(".profile-card");
  if (!card || card !== topCard() || busy) return;

  dragging = true;
  activeCard = card;
  startX = event.clientX;
  dragX = 0;
  card.classList.add("dragging");
  card.setPointerCapture(event.pointerId);   // keep following the pointer even outside the card
});

deck.addEventListener("pointermove", function (event) {
  if (!dragging) return;

  dragX = event.clientX - startX;
  activeCard.style.transform = "translateX(" + dragX + "px) rotate(" + dragX / 15 + "deg)";

  // fade in HELPFUL when dragging right, NOPE when dragging left
  activeCard.querySelector(".stamp-yes").style.opacity = Math.min(Math.max(dragX / 100, 0), 1);
  activeCard.querySelector(".stamp-no").style.opacity = Math.min(Math.max(-dragX / 100, 0), 1);
});

function endDrag() {
  if (!dragging) return;
  dragging = false;
  const card = activeCard;
  activeCard = null;

  if (Math.abs(dragX) > 100) {
    fling(dragX > 0 ? 1 : -1);           // dragged far enough: send it away
  } else {
    card.classList.remove("dragging");   // not far enough: snap back
    card.style.transform = "";
    card.querySelector(".stamp-yes").style.opacity = "";
    card.querySelector(".stamp-no").style.opacity = "";
  }
  dragX = 0;
}

deck.addEventListener("pointerup", endDrag);
deck.addEventListener("pointercancel", endDrag);

// "Start again" button
deck.addEventListener("click", function (event) {
  if (event.target.id === "resetBtn") {
    deck.innerHTML = initialDeck;
    helpful = 0;
    notHelpful = 0;
    updateTally();
    swipeMsg.textContent = "Drag a card or use the buttons.";   // CHANGED
    swipeMsg.className = "swipe-msg";                           // CHANGED
  }
});