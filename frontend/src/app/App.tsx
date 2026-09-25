import { lazy, Suspense } from "react";
import { createBrowserRouter, RouterProvider } from "react-router-dom";

import { PageSkeleton } from "../components/ui";
import { AppShell } from "./AppShell";
import { ErrorBoundary } from "./ErrorBoundary";

const HomePage = lazy(() => import("../pages/HomePage"));
const AssessmentPage = lazy(() => import("../pages/AssessmentPage"));
const ResultPage = lazy(() => import("../pages/ResultPage"));
const ScenarioLabPage = lazy(() => import("../pages/ScenarioLabPage"));
const DashboardPage = lazy(() => import("../pages/DashboardPage"));
const HistoryPage = lazy(() => import("../pages/HistoryPage"));
const CaseDetailPage = lazy(() => import("../pages/CaseDetailPage"));
const ModelPage = lazy(() => import("../pages/ModelPage"));
const AboutPage = lazy(() => import("../pages/AboutPage"));
const NotFoundPage = lazy(() => import("../pages/NotFoundPage"));

const withSuspense = (element: React.ReactNode) => <Suspense fallback={<PageSkeleton />}>{element}</Suspense>;

const router = createBrowserRouter([
  {
    element: <AppShell />,
    children: [
      { path: "/", element: withSuspense(<HomePage />) },
      { path: "/assess/new", element: withSuspense(<AssessmentPage />) },
      { path: "/assess/:id/result", element: withSuspense(<ResultPage />) },
      { path: "/scenario-lab", element: withSuspense(<ScenarioLabPage />) },
      { path: "/dashboard", element: withSuspense(<DashboardPage />) },
      { path: "/history", element: withSuspense(<HistoryPage />) },
      { path: "/history/:id", element: withSuspense(<CaseDetailPage />) },
      { path: "/model", element: withSuspense(<ModelPage />) },
      { path: "/about", element: withSuspense(<AboutPage />) },
      { path: "*", element: withSuspense(<NotFoundPage />) },
    ],
  },
]);

export function App() {
  return <ErrorBoundary><RouterProvider router={router} /></ErrorBoundary>;
}
