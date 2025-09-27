import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from './App';

// Mock the API service to avoid network calls in tests
jest.mock('./services/api');

test('renders Smart Doc Checker title', () => {
  render(<App />);
  const titleElement = screen.getByText(/smart doc checker/i);
  expect(titleElement).toBeInTheDocument();
});

test('renders file upload section', () => {
  render(<App />);
  const uploadSection = screen.getByText(/upload document/i);
  expect(uploadSection).toBeInTheDocument();
});

test('app renders without crashing', () => {
  const div = document.createElement('div');
  render(<App />);
});