let id = 0;
window.nextId = () => ++id;

window.runCode = (code) => {
  try {
    const results = generate(code);

    console.log(JSON.parse(results));
  } catch (error) {
    const er = showTraceback(error, '' + error);
    console.log(JSON.parse(er));
  }
};
