/*
 * main2.js
 *FRuck You
 */

var app=new Vue({
  el: '#app',

  data() {
  	return {
      user:  '',
      list: '',
      listItem: '',
      authenticated: false,
      cloak: false,
      status: '',
      username: '',
      password: '',
      toDoItemInput: '',
      toDoItem: '',
      userID: '',
      token: '',
  		output: {
  			response: ''
  		}
    }
},

created: function (){
  this.getToDoItem();
},
  methods:{
    //Checks to see if logged in GET
    loginCheck(){
      axios.get('http://info3103.cs.unb.ca:51327/signin')
      .then(response => {
        if(response.status = 200) {
          this.authenticated = true
          this.loggedin = response.data
          this.status= response.data.status
          //this.userID= response.data.userid.userID
          console.log(response.data)
        }
      }).catch(error => {
        this.authenticated = false
        console.log(error)
      })
      },
    //login POST
   	login(username, password){
      var app=this;
      let axiosConfig = {
        withCredentials: true,
        headers: {
          'Content-Type': 'application/json;charset=UTF-8',
          "Access-Control-Allow-Origin": "*",
          "access-Control-Allow-Credentials": "true"
        }
      };
    	axios.post('http://info3103.cs.unb.ca:51327/signin',
      {'username': this.username, 'password': this.password})
    	.then(response => {
  			console.log(response.data);
  			if(response.status == 201) {
  				this.authenticated = true
  				this.loggedin = response.data
          this.status= response.data.status
          this.userID= response.data.userid.userID
          //Don't think this post parameter is correct
  			}
  		}).catch(error => {
  			console.log(error)
        this.status= error.message
  		})

  	},
  	logout(){
  		axios.delete('http://info3103.cs.unb.ca:51327/signin')
  		.then(response => {
  			console.log(response)
  			this.authenticated = false
        this.status= response.data.status
        this.token = ''
  		}).catch(error => {
  			console.log(error)
        this.status= error.message
  		})
  	},//End of Logout
    //Gets the lists of all users
    getToDoItem(){
      var app=this;
      this.cloak = false
      axios.get('http://info3103.cs.unb.ca:51327/users/toDoList')
      .then(function (response){
        console.log(response.data);
    		if(response.status = 200) {
          app.user=response.data
    			this.status= response.data.status
          this.user=response.data.ToDoListsofAllUsers
    			console.log(response.data)
    		}
    	}).catch(function (error){
    		console.log(error)
    	});
  },
  //Gets the lists of all users
  getToDoItemOneUser(){
    var app=this;
    this.cloak = true
    axios.get('http://info3103.cs.unb.ca:51327/users/'+this.userID+'/toDoList')
    .then(function (response){
      console.log(response.data);
      if(response.status = 200) {
        app.user=response.data
        this.status= response.data.status
        this.user=response.data.ToDoListsofOneUsers
        console.log(response.data)
      }
    }).catch(function (error){
      console.log(error)
    });
},//end of getToDoItem
  //Adds a to do item
  addToDoitem(toDoItemInput){
    var app=this;
    let axiosConfig = {
      withCredentials: true,
      headers: {
        'Content-Type': 'application/json;charset=UTF-8',
        "Access-Control-Allow-Origin": "*",
        "access-Control-Allow-Credentials": "true"
      }
    };
        //Don't think this post parameter is correct
        axios.post('http://info3103.cs.unb.ca:51327/users/'+this.userID+'/toDoList/'+1,
        {'toDoItem': this.toDoItemInput})
        .then(function(response){
          console.log(response.data);
      		if(response.status = 200) {
      			this.status= response.data.status
            this.user=response.data.ToDoListsofOneUsers
      			console.log(response.data)
      		}
      	}).catch(function(error){
      		console.log(error)
      	});
    },//end of POST
    deleteOneItem(itemID){
      var app=this;
      this.itemID = itemID
  		axios.delete('http://info3103.cs.unb.ca:51327/users/'+this.userID+'/toDoList/'+this.itemID)
  		.then(function (response){
  			console.log(response)
        this.status= response.data.status
        this.token = ''
  		}).catch(function(error){
  			console.log(error)
        this.status= error.message
  		})
  	},//End of Logout
  }//end methods

})//end Vue
