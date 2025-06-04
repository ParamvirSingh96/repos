import { Navigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";
import api from "../api";
import { REFRESH_TOKEN, ACCESS_TOKEN } from "../constants";
import { useState, useEffect, useCallback } from "react";


function ProtectedRoute({ children }) {
    const [isAuthorized, setIsAuthorized] = useState(null);

    const refreshToken = useCallback(async () => {
        const refreshToken = localStorage.getItem(REFRESH_TOKEN);
        if (!refreshToken) {
            console.warn("No refresh token available to refresh session.");
            setIsAuthorized(false);
            return;
        }

        try {
            const res = await api.post("/api/token/refresh/", {
                refresh: refreshToken,
            });
            if (res.status === 200) {
                localStorage.setItem(ACCESS_TOKEN, res.data.access);
                setIsAuthorized(true);
            } else {
                console.warn(`Failed to refresh token, status: ${res.status}`);
                setIsAuthorized(false);
            }
        } catch (error) {
            console.error("Error refreshing token:", error);
            setIsAuthorized(false);
        }
    }, [setIsAuthorized]);

    const auth = useCallback(async () => {
        const token = localStorage.getItem(ACCESS_TOKEN);
        if (!token) {
            setIsAuthorized(false);
            return;
        }
        try {
            const decoded = jwtDecode(token); 
            const tokenExpiration = decoded.exp;
            const now = Date.now() / 1000;

        if (tokenExpiration < now) {
                await refreshToken(); 
            } else {
                setIsAuthorized(true);
            }
        } catch (error) {
            console.error("Error decoding token or during auth process:", error);
            setIsAuthorized(false);
        }
    }, [setIsAuthorized, refreshToken]);

    useEffect(() => {
        auth().catch((error) => {
            console.error("Unhandled error during initial auth call:", error);
            setIsAuthorized(false);
        });
    }, [auth]);

    if (isAuthorized === null) {
        return <div>Loading...</div>;
    }

    return isAuthorized ? children : <Navigate to="/login" replace />;
}

export default ProtectedRoute;