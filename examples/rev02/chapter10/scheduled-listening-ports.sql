SELECT p.name, p.path, l.port, l.address
FROM listening_ports l
JOIN processes p USING (pid)
WHERE l.protocol = 6
AND l.address NOT IN
('127.0.0.1','::1','127.0.0.53')
AND p.name NOT IN ('docker-proxy');
