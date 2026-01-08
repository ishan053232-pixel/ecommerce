const container = document.getElementById("character");

let anim = lottie.loadAnimation({
  container: container,
  renderer: "svg",
  loop: true,
  autoplay: true,
  path: "/static/lottie/idle.json"
});

function playAnimation(file, loop = true) {
  anim.destroy();
  anim = lottie.loadAnimation({
    container,
    renderer: "svg",
    loop,
    autoplay: true,
    path: `/static/lottie/${file}`
  });
}

// Input reactions
document.querySelector('input[name="username"]').addEventListener("focus", () => {
  playAnimation("look.json");
});

document.querySelector('input[name="password"]').addEventListener("focus", () => {
  playAnimation("hide.json");
});

// Back to idle
document.querySelectorAll("input").forEach(i => {
  i.addEventListener("blur", () => {
    playAnimation("idle.json");
  });
});

// Submit
document.querySelector("form").addEventListener("submit", () => {
  playAnimation("success.json", false);
});
