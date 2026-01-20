// Mock for @inquirer/prompts
const confirm = jest.fn().mockResolvedValue(true);
const input = jest.fn().mockResolvedValue('test');
const password = jest.fn().mockResolvedValue('password');
const select = jest.fn().mockResolvedValue('option1');
const checkbox = jest.fn().mockResolvedValue(['option1']);
const editor = jest.fn().mockResolvedValue('text');
const number = jest.fn().mockResolvedValue(42);
const rawlist = jest.fn().mockResolvedValue('option1');
const expand = jest.fn().mockResolvedValue('option1');

module.exports = {
  confirm,
  input,
  password,
  select,
  checkbox,
  editor,
  number,
  rawlist,
  expand,
};

