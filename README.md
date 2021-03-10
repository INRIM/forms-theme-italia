# Form Theme Italia

This reposotory is a dependency of 

Questo progetto è un componente del progetto più ampio di un gruppo
di micro servizi mirati all'integrazione con U-GOV, è possibile attivarli
singolarmente in modo modulare, e attivarne molteplici in modo scalare in caso di necessità


## Come iniziare

Clonare il progetto

- #### Configurazione 
    - creare una copia di .env.example:
      ```
        cp .env.example  .env
        ```
      ```
        cp .env.example  .env-test
        ```
- #### Url Ambienti U-GOV

  Editare la chiave `BASE_URL_WS` file .env inserendo la url di pre-prod in .env-test
  e prod in .env di U-GOV, come descritto nelle linee guida della documentazione del Technical Portal di U-GOV
  
- #### JWT Token e Autenticazione WS U-GOV
    
  Al fine di utilizzare i WS U-GOV è necessario attivare un utente tecnico abilitato allo scopo sullo stesso U'GOV.

  Abilitato l'utente U-GOV è necessario creare un token [JWT](https://jwt.io/) con tali informazioni da inviare alle API:
  
    - editare `JWT_SECRET` nel file .env aggiungendo la chiave segreta
      
      - e' possibile generare una chiave compatibile digitando: 
        ```
        openssl rand -hex 32
        ```
        
    - il token JWT, nel payload deve contenere:
      
      - ```
        {
            "sub": ugov_tech_user_name,
            "pass": ugov_tech_user_pass
        }
        ```
  - tuttavia e' possibile generare un token pronto all'uso eseguendo una chiamata in post al
    servizio: {url}/genera-token
    
    - ```
      payload:
      
      {
            "user": ugov_tech_user_name,
            "pass": ugov_tech_user_pass,
            "secret": secret_key,
            "alg": HS256
      }
      ```
    
- #### Ambiente di Sviluppo
    
    Assicurarsi di avere Docker Installato
    
    Se necessario modificare il binding porta 8022 e 9022
  
    ```
    sh build_and_run.sh
    ```
  
    il servizio si avvia prod  http://localhost:8022/persona-fisica/
    il servizio si avvia test  http://localhost:9022/persona-fisica/
  
    lo script abilita autoreload dei file per semplificare la fase di sviluppo


- #### Ambiente di Test / Pre-Produzione

  Per convenzione del progetto l'ambiete di test e' risponde sulla porta 9022

- #### Ambiente di Produzione

  Per convenzione del progetto l'ambiete di test e' risponde sulla porta 8022


## Documentazione e Test delle Api

Una volta avviato il progetto la documentazione delle API è disponibile agli url:

- {BASE_URL}:8022/persona-fisica/redoc ( Redoc )
- {BASE_URL}:8022/persona-fisica/docs ( Swagger )

Tramite la Documentazione Swagger e' possibile testare le API:

- {BASE_URL}:8022/persona-fisica/docs (da bloccare in ambiente di prod )
- {BASE_URL}:9022/persona-fisica/docs

Per eseguire i test è necessario inserire come parametro header il token JWT generato

## Costruito con

* [FormioJs](https://github.com/formio/formio.js) -  SDK for Form.io
* [Jinja](https://github.com/pallets/jinja) - Jinja is a fast, expressive, extensible templating engine 

## Versionamento

Usiamo [SemVer](http://semver.org/) per il versionamento. Versioni disponibili, vedere [tags in questo repository](https://github.com/INRIM/api-ugov-persona-fisica/tags). 


## Licenza

api-ugov-persona-fisica è rilasciato con [licenza MIT](https://github.com/INRIM/api-ugov-persona-fisica/blob/master/LICENSE).