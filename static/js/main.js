// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 评论框显示/隐藏
    const commentBtns = document.querySelectorAll('.comment-btn');
    commentBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const postId = this.getAttribute('data-post-id');
            const commentBox = document.getElementById(`comment-box-${postId}`);
            if (commentBox.style.display === 'none' || commentBox.style.display === '') {
                commentBox.style.display = 'block';
            } else {
                commentBox.style.display = 'none';
            }
        });
    });

    // 点赞按钮点击事件
    const likeBtns = document.querySelectorAll('.like-btn');
    likeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const postId = this.getAttribute('data-post-id');
            // 提交点赞表单
            document.getElementById(`like-form-${postId}`).submit();
        });
    });

    // 关闭提示框
    const alertCloseBtns = document.querySelectorAll('.btn-close');
    alertCloseBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            this.parentElement.style.display = 'none';
        });
    });

    // 图片预览（上传前）
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                // 仅为用户体验，可选
                const fileName = this.files[0].name;
                console.log(`已选择文件：${fileName}`);
            }
        });
    });
});