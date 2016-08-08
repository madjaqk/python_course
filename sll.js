function slNode(val){
	this.value = val
	this.next = null
}

function slList(){
	this.head = null

	this.add_to_front = function(val){
		var temp = this.head
		this.head = new slNode(val)
		this.head.next = temp

		return this
	}

	this.add_to_back = function(val){
		if(!this.head){
			this.head = new slNode(val)
		} else {
			var runner = this.head
			while(runner.next){
				runner = runner.next
			}

			runner.next = new slNode(val)
		}

		return this
	}

	this.print = function(){
		var runner = this.head
		var output = ""

		while(runner){
			output += `[${runner.value}] ==> `
			runner = runner.next
		}

		console.log(output)
		return output
	}

	this.contains = function(target){
		var runner = this.head

		while(runner){
			if(runner.value === target){
				return true
			} else {
				runner = runner.next
			}
		}

		return false
	}

	this.remove = function(target){
		if(this.head){
			if(this.head.value === target){
				this.head = this.head.next
				return this
			}
			
			var runner = this.head
			while(runner.next){
				if(runner.next.value === target){
					runner.next = runner.next.next
					return this
				}
				runner = runner.next
			}
		}

		return false
	}
}

var my_list = new slList()

my_list.add_to_back(5).add_to_back(1).add_to_front(7).add_to_back(4).print()

for(var i = 1; i <= 8; i++){
	if(my_list.contains(i)){
		console.log(i + ": YES")
	} else {
		console.log(i + ": NO")
	}
}

my_list.remove(5).remove(7).print()

