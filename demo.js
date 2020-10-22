let id = 0;
window.nextId = () => ++id;

window.runCode = (code) => {
  const results = generate(code);

  console.log(JSON.parse(results));
};
