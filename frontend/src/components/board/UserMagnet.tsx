import { Delete } from "@mui/icons-material";
import { Card, IconButton, Typography } from "@mui/material";

import { useDeleteUserMutation } from "@/state/apiSlice";
import { User } from "@/types";

interface UserMagnetProps {
    user: User;
    editable: boolean;
}

const UserMagnet: React.FC<UserMagnetProps> = ({ user, editable }) => {

    const [deleteUser] = useDeleteUserMutation();

    const handleDelete = () => {
        deleteUser({ userId: user.userid });
    };

    return (
        <Card sx={{
            display: "flex",
            justifyContent: "center",
            backgroundColor: editable ? "rgb(230,170,170)" : user.color || "rgb(230,247,206)",
            alignItems: "center", margin: "5px", border: "solid 1px", borderRadius: "10px", color: "black", width: editable ? "70px":  "60px", overflow: "hidden", height:"20px"
        }}>
            <Typography sx={{
                fontSize: "13px",
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
                display: "inline-block",
                }}>{user.name}</Typography>
        {editable && //can later show a form to change user color, name, delete etc
         <IconButton size="small"  title="Delete User" onClick={() => handleDelete()}>
            <Delete style={{ fontSize: 18, }}/>
         </IconButton>
         }
        </Card>
    );
};

export default UserMagnet;