export default {
  testEnvironment: 'jsdom',
  moduleFileExtensions: ['js'],
  testMatch: ['**/public/src/tests/**/*.test.js'],
  coverageDirectory: 'coverage',
  collectCoverageFrom: ['public/src/**/*.js'],
  transform: {},
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js']
};
