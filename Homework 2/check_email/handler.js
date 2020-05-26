const connect_to_db = require('./db'); //Carico il DB - file db.js

// GET BY TALK HANDLER

const user = require('./Users'); //Carico il modello dati - file Talk.js
//get_by_tag è il nome da mettere nel gestore
module.exports.get_email = (event, context, callback) => { 
    context.callbackWaitsForEmptyEventLoop = false;
    console.log('Received event:', JSON.stringify(event, null, 2));
    let body = {}
    if (event.body) {
        body = JSON.parse(event.body) //Trasformo il contenuto dell'evento e faccio il parse a JSON
    }//event.body è in formato stringa.
    // set default
    if(!body.mail) {
        callback(null, {
                    statusCode: 500,
                    headers: { 'Content-Type': 'text/plain' },
                    body: 'Could not fetch the uploader. Email is null.'
        })
    }
    
    
    connect_to_db().then(() => { //questa funzione era già stata definita all'interno del file db.js
        console.log('=> get watch nexts:');
        talk.find({_id: body.idx}) //la sintassi è la stessa delle query su mongo DB
            .then(talks => { //per tutti i talk tornati va a tradurre 
                    callback(null, {
                        statusCode: 200,
                        body: JSON.stringify(talks)
                    })
                }
            )
            .catch(err => //in caso di errore fa questa funzione
                callback(null, {
                    statusCode: err.statusCode || 500,
                    headers: { 'Content-Type': 'text/plain' },
                    body: 'Could not fetch the uploader in TEDx media uploader list.'
                })
            );
    });
};
