import { BoardState } from './types'

export const initialBoardState: BoardState = {
  columns: [
    { id: 'backlog', title: 'Backlog', cardIds: ['c1', 'c2'] },
    { id: 'todo', title: 'To Do', cardIds: ['c3', 'c4', 'c5'] },
    { id: 'in-progress', title: 'In Progress', cardIds: ['c6', 'c7'] },
    { id: 'review', title: 'Review', cardIds: ['c8'] },
    { id: 'done', title: 'Done', cardIds: ['c9', 'c10'] },
  ],
  cards: {
    c1: { id: 'c1', title: 'Design system', details: 'Create reusable component library with colors, typography, and spacing tokens' },
    c2: { id: 'c2', title: 'API documentation', details: 'Document all REST endpoints with request/response examples' },
    c3: { id: 'c3', title: 'User authentication', details: 'Implement login/signup flow with JWT tokens' },
    c4: { id: 'c4', title: 'Dashboard layout', details: 'Build responsive dashboard with sidebar navigation' },
    c5: { id: 'c5', title: 'Database schema', details: 'Design and migrate PostgreSQL schema for core entities' },
    c6: { id: 'c6', title: 'Search feature', details: 'Implement full-text search across products with filtering' },
    c7: { id: 'c7', title: 'Payment integration', details: 'Integrate Stripe checkout for subscription plans' },
    c8: { id: 'c8', title: 'Email templates', details: 'Design responsive email templates for notifications' },
    c9: { id: 'c9', title: 'Landing page', details: 'Build marketing landing page with hero and features section' },
    c10: { id: 'c10', title: 'CI/CD pipeline', details: 'Set up GitHub Actions for automated testing and deployment' },
  },
  columnOrder: ['backlog', 'todo', 'in-progress', 'review', 'done'],
}
