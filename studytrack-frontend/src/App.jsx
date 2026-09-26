import Dashboard from "./pages/Dashboard";
import Analytics from "./pages/Analytics";


function App() {

    const path = window.location.pathname;


    if (path === "/analytics") {
        return <Analytics />;
    }


    return <Dashboard />;
}


export default App;
