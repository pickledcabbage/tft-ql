
export type SessionData = {
    user_id: string,
    session_id: string,
    connected: boolean,
    join_code: string,
};

export const createEmptySessionData = () => {
    return {
        user_id: '',
        session_id: '',
        connected: false,
        join_code: '',
    }
}
