// CONNECTION TO DB

const mongoose = require('mongoose');
mongoose.Promise = global.Promise;
let isConnected; //viene salvato lo stato della connessione


require('dotenv').config({ path: './variables.env' });

module.exports = connect_to_db = () => {
    if (isConnected) { //se la connessione è già stata fatta usa quella
        console.log('=> using existing database connection');
        return Promise.resolve();
    }
    //altrimenti utilizzo una nuova connessione
    console.log('=> using new database connection');
    return mongoose.connect(process.env.DB, {dbName: 'unibg_tedx', useNewUrlParser: true, useUnifiedTopology: true}).then(db => {
        isConnected = db.connections[0].readyState;
    });
};