/**
 * Arquivo de teste React/TypeScript com problemas propositais
 */

import React, { useState, useEffect } from 'react';

// ❌ console.log em produção
console.log('Debug mode');

// ❌ Componente sem PropTypes/TypeScript types
function UserCard({ user }) {
  // ❌ useEffect sem dependências
  useEffect(() => {
    fetchUserData();
  });
  
  // ❌ var ao invés de const/let
  var count = 0;
  
  return (
    <div>
      <h1>{user.name}</h1>
    </div>
  );
}

// ❌ Lista sem keys
function UserList({ users }) {
  return (
    <div>
      {users.map(user => (
        <div>{user.name}</div>
      ))}
    </div>
  );
}

// ❌ Componente muito longo (> 300 linhas)
function Dashboard() {
  const [data, setData] = useState([]);
  
  // Muitas linhas de código...
  const line1 = 1;
  const line2 = 2;
  const line3 = 3;
  // ... imagine 300+ linhas aqui
  
  return <div>Dashboard</div>;
}

// ❌ Hook customizado sem 'use' prefix
function customHook() {
  const [value, setValue] = useState(0);
  return [value, setValue];
}

// ❌ Uso de 'any' em TypeScript
function processData(data: any): any {
  return data;
}

// ✅ Componente correto
interface UserProps {
  user: {
    id: number;
    name: string;
  };
}

const CorrectUserCard: React.FC<UserProps> = ({ user }) => {
  useEffect(() => {
    // Código
  }, [user.id]);
  
  return (
    <div>
      <h1>{user.name}</h1>
    </div>
  );
};

// ✅ Lista com keys
const CorrectUserList: React.FC<{ users: UserProps['user'][] }> = ({ users }) => {
  return (
    <div>
      {users.map(user => (
        <div key={user.id}>{user.name}</div>
      ))}
    </div>
  );
};

export { UserCard, UserList, Dashboard, CorrectUserCard, CorrectUserList };

// Made with Bob
