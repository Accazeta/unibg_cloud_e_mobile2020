const mongoose = require('mongoose'); //carico la libreria mongoose

const Uploader_schema = new mongoose.Schema({ //definisce lo schema che ho su mongoDB
    email: String,
    main_speaker : String,
    idxVideo : [String]
}, { collection: 'tedx_uploader_email' });

module.exports = mongoose.model('user', Uploader_schema); //esporto il modello così ce l'ho in esposizione all'interno del mio modulo